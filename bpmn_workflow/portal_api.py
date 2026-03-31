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

# --- Mixins ---

class WorkflowMixin:
    """
    A mixin for handling common state transition logic.
    Handles the execution of task completion and moves the process forward.
    """
    
    @transaction.atomic
    def perform_task_transition(self, task_instance, user, data):
        """
        Triggers the state transition in the BPMN engine.
        """
        try:
            BPMNEngine.complete_task(task_instance, user, data)
            return True, _("Task completed successfully.")
        except PermissionError as e:
            return False, str(e)
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            logger.exception("Error during workflow transition")
            return False, _("An unexpected error occurred during the workflow transition.")

# --- Dashboard Views ---

class DashboardSummaryView(APIView):
    """
    Returns counts for waiting tasks, active requests, and archived items.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # waiting_tasks_count: Tasks assigned to request.user with status Ready or In Progress
        waiting_tasks_count = TaskInstance.objects.filter(
            assignee=user,
            status__in=['ready', 'in_progress']
        ).count()
        
        # active_requests_count: Processes started by request.user that are not yet COMPLETED/TERMINATED
        active_requests_count = ProcessInstance.objects.filter(
            started_by=user,
            status='active'
        ).count()
        
        # archived_count: Finished processes by the user
        archived_count = ProcessInstance.objects.filter(
            started_by=user,
            status__in=['completed', 'terminated']
        ).count()

        return Response({
            'waiting_tasks_count': waiting_tasks_count,
            'active_requests_count': active_requests_count,
            'archived_count': archived_count,
        })

# --- Portal ViewSets ---

class EmployeePortalViewSet(viewsets.ModelViewSet):
    """
    Handles 'My Requests' and 'Archive' for the employee.
    Include creation of new requests.
    """
    serializer_class = ProcessInstanceSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Expected data: { "workflow_key": "...", "variables": {...}, "content_type": ..., "object_id": ... }
        data = self.request.data
        workflow_key = data.get('workflow_key')
        variables = data.get('variables', {})
        content_type_id = data.get('content_type')
        object_id = data.get('object_id')
        
        if not workflow_key or not content_type_id or not object_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(_("workflow_key, content_type and object_id are required."))

        # Versioning: Ensure new requests use the latest active version
        workflow = WorkflowDefinition.objects.filter(
            key=workflow_key, 
            is_active=True
        ).order_by('-version').first()
        
        if not workflow:
            from rest_framework.exceptions import NotFound
            raise NotFound(_("No active workflow found for key: {key}").format(key=workflow_key))

        from django.contrib.contenttypes.models import ContentType
        try:
            ct = ContentType.objects.get(pk=content_type_id)
            business_object = ct.get_object_for_this_type(pk=object_id)
        except Exception:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(_("Invalid content_type or object_id."))

        # Atomic process initiation
        with transaction.atomic():
            process = BPMNEngine.start_process(
                workflow.key, 
                business_object, 
                self.request.user, 
                variables
            )
            return process

    def create(self, request, *args, **kwargs):
        process = self.perform_create(None)
        serializer = self.get_serializer(process)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        # Row-Level Security: Employees only see their own requests
        user = self.request.user
        queryset = ProcessInstance.objects.filter(started_by=user).select_related('workflow', 'started_by')
        
        # Optional Tab-based filtering
        status_param = self.request.query_params.get('status')
        if status_param == 'active':
            queryset = queryset.filter(status='active')
        elif status_param == 'archived':
            queryset = queryset.filter(status__in=['completed', 'terminated'])
            
        return queryset.order_by('-started_at')

    def list(self, request, *args, **kwargs):
        """
        Optimized list with progress_percentage calculation.
        """
        response = super().list(request, *args, **kwargs)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data

        for item in results:
            instance_id = item.get('id')
            instance = ProcessInstance.objects.get(id=instance_id)
            
            total_nodes = instance.workflow.nodes.count()
            # Calculate progress based on unique nodes visited in logs
            visited_nodes_count = instance.activity_logs.filter(
                node__isnull=False
            ).values('node').distinct().count()
            
            progress = (visited_nodes_count / total_nodes * 100) if total_nodes > 0 else 0
            item['progress_percentage'] = round(min(progress, 100), 2)
            
        return response

class TaskInboxViewSet(viewsets.ReadOnlyModelViewSet, WorkflowMixin):
    """
    Handles the Waiting Tasks list and Task actions.
    """
    serializer_class = TaskInstanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = TaskInstance.objects.filter(
            assignee=user,
            status__in=['ready', 'in_progress']
        ).select_related(
            'process_instance__workflow', 'node', 'assignee'
        )

        urgent = self.request.query_params.get('urgent')
        if urgent == 'true':
            near_deadline = timezone.now() + timezone.timedelta(hours=24)
            queryset = queryset.filter(due_date__lte=near_deadline)
            
        return queryset

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """
        Claim a task if it's in 'ready' state.
        """
        task = self.get_object()
        if task.status != 'ready':
            return Response(
                {'error': _("Task is already claimed or completed.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save()
        
        return Response({'status': _("Task claimed successfully.")})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Complete a task and trigger state transition.
        """
        task = self.get_object()
        data = request.data.get('data', {})
        
        success, message = self.perform_task_transition(task, request.user, data)
        
        if success:
            return Response({'status': message})
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

# --- Timeline View ---

class ProcessTimelineView(APIView):
    """
    Returns the full audit trail of a process instance for the vertical UI timeline.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        process = get_object_or_404(ProcessInstance, pk=pk)
        
        # Row-Level Security
        if process.started_by != request.user and not request.user.is_staff:
             return Response({'error': _("Permission denied.")}, status=status.HTTP_403_FORBIDDEN)

        logs = process.activity_logs.select_related('actor', 'node').order_by('timestamp')
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data)

# --- Messaging Views ---

class CommentViewSet(viewsets.ModelViewSet):
    """
    Allows employees to leave notes or ask questions on a specific request.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        process_id = self.request.query_params.get('process_instance')
        if not process_id:
            return Comment.objects.none()
        
        process = get_object_or_404(ProcessInstance, pk=process_id)
        
        # Row-Level Security
        if process.started_by != self.request.user and not self.request.user.is_staff:
            return Comment.objects.none()

        return Comment.objects.filter(
            process_instance=process
        ).select_related('author').order_by('-created_at')

    def perform_create(self, serializer):
        process_id = self.request.data.get('process_instance')
        process = get_object_or_404(ProcessInstance, id=process_id)
        serializer.save(author=self.request.user, process_instance=process)
