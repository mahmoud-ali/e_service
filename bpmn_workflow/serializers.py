from rest_framework import serializers
from .models import WorkflowDefinition, ProcessInstance, TaskInstance, BPMNNode, Token, ActivityLog, Comment

class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowDefinition
        fields = ['id', 'key', 'name', 'description', 'version', 'is_active', 'created_at', 'updated_at']


class ProcessInstanceSerializer(serializers.ModelSerializer):
    workflow_name = serializers.ReadOnlyField(source='workflow.name')
    
    class Meta:
        model = ProcessInstance
        fields = ['id', 'workflow', 'workflow_name', 'status', 'variables', 'started_by', 'started_at', 'ended_at']
        read_only_fields = ['started_by', 'started_at', 'ended_at']


class TaskInstanceSerializer(serializers.ModelSerializer):
    node_name = serializers.ReadOnlyField(source='node.name')
    workflow_name = serializers.ReadOnlyField(source='process_instance.workflow.name')
    
    class Meta:
        model = TaskInstance
        fields = [
            'id', 'process_instance', 'workflow_name', 'node', 'node_name', 
            'status', 'assignee', 'input_data', 'output_data', 'created_at', 'due_date'
        ]
        read_only_fields = ['created_at']


class ActivityLogSerializer(serializers.ModelSerializer):
    node_name = serializers.ReadOnlyField(source='node.name')
    actor_name = serializers.ReadOnlyField(source='actor.username')
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'event_type', 'event_type_display', 'node', 'node_name', 
            'actor', 'actor_name', 'details', 'timestamp'
        ]

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'process_instance', 'author', 'author_name', 'text', 'created_at']
        read_only_fields = ['author', 'created_at']
