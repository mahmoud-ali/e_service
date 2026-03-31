from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

import logging

from .models import (
    WorkflowDefinition, 
    ProcessInstance, 
    TaskInstance, 
    Token, 
    ActivityLog, 
    Comment,
    BPMNNode
)
from .serializers import (
    WorkflowDefinitionSerializer, 
    ProcessInstanceSerializer, 
    TaskInstanceSerializer,
    ActivityLogSerializer,
    CommentSerializer
)
from .engine import BPMNEngine

User = get_user_model()
logger = logging.getLogger(__name__)

# --- Core Engine ViewSets ---

class WorkflowViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Workflow Definitions.
    """
    queryset = WorkflowDefinition.objects.all()
    serializer_class = WorkflowDefinitionSerializer
    lookup_field = 'key'
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='import')
    def import_workflow(self, request):
        """
        Import or update a workflow definition from XML.
        """
        key = request.data.get('key')
        xml_content = request.data.get('xml')
        
        if not key or not xml_content:
            return Response(
                {'error': _('Both "key" and "xml" are required.')}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            from .importer import WorkflowSyncService
            workflow, created = WorkflowDefinition.objects.update_or_create(
                key=key,
                defaults={
                    'bpmn_xml': xml_content,
                    'name': request.data.get('name', key.replace('_', ' ').title())
                }
            )
            WorkflowSyncService.sync(workflow)
            
            return Response({
                'status': _('Workflow imported successfully'),
                'id': workflow.id,
                'key': workflow.key,
                'nodes_count': workflow.nodes.count()
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start(self, request, key=None):
        """
        Starts a new ProcessInstance for this workflow.
        """
        workflow = self.get_object()
        data = request.data
        variables = data.get('variables', {})
        
        content_type_id = data.get('content_type')
        object_id = data.get('object_id')
        
        if not content_type_id or not object_id:
            return Response(
                {'error': _('content_type and object_id are required to start a process instance.')}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from django.contrib.contenttypes.models import ContentType
            ct = ContentType.objects.get(pk=content_type_id)
            business_object = ct.get_object_for_this_type(pk=object_id)
            
            process = BPMNEngine.start_process(workflow.key, business_object, request.user, variables)
            serializer = ProcessInstanceSerializer(process)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProcessInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing and managing Process Instances.
    """
    queryset = ProcessInstance.objects.all()
    serializer_class = ProcessInstanceSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'], url_path='execute')
    def execute(self, request, pk=None):
        process = self.get_object()
        error_tokens = process.tokens.filter(status='error', is_active=True)
        processed_count = 0
        
        if not error_tokens.exists():
            return Response({'status': _('No error tokens found to retry')})

        for token in error_tokens:
            token.status = 'active'
            token.save()
            try:
                BPMNEngine._move_token(token, request.user)
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to retry token {token.id}: {e}")
        
        return Response({'status': _('Retried {count} tokens').format(count=processed_count)})

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        process = self.get_object()
        logs = process.activity_logs.all().order_by('timestamp')
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing and completing Task Instances.
    """
    queryset = TaskInstance.objects.all()
    serializer_class = TaskInstanceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def active(self, request):
        tasks = TaskInstance.objects.filter(
            status__in=['ready', 'in_progress'],
            assignee=request.user
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = get_object_or_404(TaskInstance, pk=pk)
        data = request.data.get('data', {})
        
        try:
            BPMNEngine.complete_task(task, request.user, data)
            return Response({'status': _('Task completed successfully')})
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error completing task")
            return Response({'error': _("Unexpected error: {error}").format(error=str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
