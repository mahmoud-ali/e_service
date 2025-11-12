"""
BPMN Workflow Models

Models for representing BPMN processes, instances, and execution state.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import uuid

User = get_user_model()


class WorkflowDefinition(models.Model):
    """BPMN Process Definition"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.SlugField(max_length=100, unique=True, help_text="Unique identifier for this workflow")
    name = models.CharField(max_length=200, help_text="Human-readable name")
    description = models.TextField(blank=True)
    
    # BPMN specific
    bpmn_xml = models.TextField(help_text="Original BPMN 2.0 XML content")
    bpmn_process_id = models.CharField(max_length=200, help_text="Process ID from BPMN file")
    handler_class = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Python path to handler class (e.g., 'bpmn_workflow.handlers.MyHandler')"
    )
    
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Workflow Definition'
        verbose_name_plural = 'Workflow Definitions'
        unique_together = [['key', 'version']]
        ordering = ['-version']

    def __str__(self):
        return f"{self.name} (v{self.version})"


class BPMNNode(models.Model):
    """BPMN Element (Task, Gateway, Event)"""
    
    NODE_TYPES = [
        # Events
        ('start_event', 'Start Event'),
        ('end_event', 'End Event'),
        ('intermediate_event', 'Intermediate Event'),
        
        # Tasks
        ('user_task', 'User Task'),
        ('service_task', 'Service Task'),
        ('script_task', 'Script Task'),
        ('send_task', 'Send Task'),
        ('receive_task', 'Receive Task'),
        
        # Gateways
        ('exclusive_gateway', 'Exclusive Gateway'),
        ('parallel_gateway', 'Parallel Gateway'),
        ('inclusive_gateway', 'Inclusive Gateway'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE, related_name='nodes')
    
    # BPMN attributes
    bpmn_id = models.CharField(max_length=200, help_text="ID from BPMN XML")
    node_type = models.CharField(max_length=30, choices=NODE_TYPES)
    name = models.CharField(max_length=200)
    
    # For UserTasks
    assignee_expression = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Expression to determine assignee (e.g., '${department.manager}')"
    )
    candidate_groups = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of group names that can claim this task"
    )
    form_key = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Reference to Django form class"
    )
    
    # For ServiceTasks
    implementation = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Python function path for service tasks"
    )
    
    # For Gateways
    default_flow = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="BPMN ID of default sequence flow"
    )
    
    # Custom properties from BPMN extensions
    properties = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'BPMN Node'
        verbose_name_plural = 'BPMN Nodes'
        unique_together = [['workflow', 'bpmn_id']]

    def __str__(self):
        return f"{self.name} ({self.node_type})"


class SequenceFlow(models.Model):
    """BPMN Sequence Flow (Transition between nodes)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE, related_name='flows')
    
    bpmn_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200, blank=True)
    
    source = models.ForeignKey(BPMNNode, on_delete=models.CASCADE, related_name='outgoing_flows')
    target = models.ForeignKey(BPMNNode, on_delete=models.CASCADE, related_name='incoming_flows')
    
    # Condition for exclusive gateways
    condition_expression = models.TextField(
        blank=True,
        null=True,
        help_text="Python expression for flow condition"
    )
    
    # Priority for ordering
    priority = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sequence Flow'
        verbose_name_plural = 'Sequence Flows'
        unique_together = [['workflow', 'bpmn_id']]
        ordering = ['priority']

    def __str__(self):
        return f"{self.source.name} → {self.target.name}"


class ProcessInstance(models.Model):
    """Runtime instance of a BPMN process"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(WorkflowDefinition, on_delete=models.PROTECT)
    
    # Generic relation to business object (NeedsRequest, LeaveRequest, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Process variables (can be accessed in expressions)
    variables = models.JSONField(default=dict, help_text="Process-level variables")
    
    # Tracking
    started_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='started_processes')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Process Instance'
        verbose_name_plural = 'Process Instances'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['status']),
            models.Index(fields=['-started_at']),
        ]

    def __str__(self):
        return f"{self.workflow.name} - {self.content_object} ({self.status})"

    def get_active_tokens(self):
        """Get all active tokens in this process"""
        return self.tokens.filter(is_active=True)

    def get_current_tasks(self):
        """Get all active user tasks"""
        return self.tasks.filter(status__in=['ready', 'in_progress'])


class Token(models.Model):
    """Represents current position(s) in the process (execution pointer)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    process_instance = models.ForeignKey(ProcessInstance, on_delete=models.CASCADE, related_name='tokens')
    current_node = models.ForeignKey(BPMNNode, on_delete=models.CASCADE)
    
    is_active = models.BooleanField(default=True)
    
    # For parallel gateways - track parent token
    parent_token = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='child_tokens'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'
        indexes = [
            models.Index(fields=['process_instance', 'is_active']),
        ]

    def __str__(self):
        status = "active" if self.is_active else "completed"
        return f"Token at {self.current_node.name} ({status})"


class TaskInstance(models.Model):
    """Instance of a UserTask or ServiceTask"""
    
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('ready', 'Ready'),
        ('reserved', 'Reserved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    process_instance = models.ForeignKey(ProcessInstance, on_delete=models.CASCADE, related_name='tasks')
    node = models.ForeignKey(BPMNNode, on_delete=models.PROTECT)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    
    # Assignment
    assignee = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tasks'
    )
    candidate_users = models.ManyToManyField(User, blank=True, related_name='candidate_tasks')
    
    # Task data
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Task Instance'
        verbose_name_plural = 'Task Instances'
        indexes = [
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['process_instance', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.node.name} - {self.status}"

    def can_be_completed_by(self, user):
        """Check if user can complete this task"""
        if self.status not in ['ready', 'in_progress']:
            return False
        
        # Superuser can do anything
        if user.is_superuser:
            return True
        
        # Check if assigned
        if self.assignee and self.assignee == user:
            return True
        
        # Check if in candidate users
        if self.candidate_users.filter(pk=user.pk).exists():
            return True
        
        # Check if user is in candidate groups
        if self.node.candidate_groups:
            user_groups = user.groups.values_list('name', flat=True)
            if any(group in user_groups for group in self.node.candidate_groups):
                return True
        
        return False


class ActivityLog(models.Model):
    """Immutable audit log of all process activities"""
    
    EVENT_TYPES = [
        ('process_started', 'Process Started'),
        ('process_completed', 'Process Completed'),
        ('process_terminated', 'Process Terminated'),
        ('process_suspended', 'Process Suspended'),
        ('process_resumed', 'Process Resumed'),
        ('task_created', 'Task Created'),
        ('task_assigned', 'Task Assigned'),
        ('task_started', 'Task Started'),
        ('task_completed', 'Task Completed'),
        ('task_failed', 'Task Failed'),
        ('gateway_evaluated', 'Gateway Evaluated'),
        ('token_moved', 'Token Moved'),
        ('variable_set', 'Variable Set'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    process_instance = models.ForeignKey(ProcessInstance, on_delete=models.CASCADE, related_name='activity_logs')
    task_instance = models.ForeignKey(TaskInstance, on_delete=models.CASCADE, null=True, blank=True)
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    node = models.ForeignKey(BPMNNode, on_delete=models.SET_NULL, null=True, blank=True)
    
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['process_instance', '-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"
