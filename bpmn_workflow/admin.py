"""
Django Admin configuration for BPMN Workflow models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    WorkflowDefinition, BPMNNode, SequenceFlow,
    ProcessInstance, Token, TaskInstance, ActivityLog
)


class BPMNNodeInline(admin.TabularInline):
    model = BPMNNode
    extra = 0
    fields = ['bpmn_id', 'node_type', 'name', 'candidate_groups']
    readonly_fields = ['bpmn_id', 'node_type', 'name']
    can_delete = False


class SequenceFlowInline(admin.TabularInline):
    model = SequenceFlow
    extra = 0
    fields = ['bpmn_id', 'name', 'source', 'target', 'condition_expression']
    readonly_fields = ['bpmn_id', 'name', 'source', 'target']
    can_delete = False


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ['key', 'name', 'version', 'is_active', 'node_count', 'flow_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key', 'name', 'bpmn_process_id']
    readonly_fields = ['bpmn_process_id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['key', 'name', 'description', 'version', 'is_active']
        }),
        ('BPMN Details', {
            'fields': ['bpmn_process_id', 'handler_class']
        }),
        ('XML', {
            'fields': ['bpmn_xml'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    inlines = [BPMNNodeInline, SequenceFlowInline]
    
    def node_count(self, obj):
        return obj.nodes.count()
    node_count.short_description = 'Nodes'
    
    def flow_count(self, obj):
        return obj.flows.count()
    flow_count.short_description = 'Flows'


@admin.register(BPMNNode)
class BPMNNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'node_type', 'workflow', 'bpmn_id', 'outgoing_count', 'incoming_count']
    list_filter = ['node_type', 'workflow']
    search_fields = ['name', 'bpmn_id']
    readonly_fields = ['bpmn_id', 'created_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['workflow', 'bpmn_id', 'node_type', 'name']
        }),
        ('User Task Configuration', {
            'fields': ['assignee_expression', 'candidate_groups', 'form_key'],
            'classes': ['collapse']
        }),
        ('Service Task Configuration', {
            'fields': ['implementation'],
            'classes': ['collapse']
        }),
        ('Gateway Configuration', {
            'fields': ['default_flow'],
            'classes': ['collapse']
        }),
        ('Additional Properties', {
            'fields': ['properties', 'created_at'],
            'classes': ['collapse']
        }),
    ]
    
    def outgoing_count(self, obj):
        return obj.outgoing_flows.count()
    outgoing_count.short_description = 'Outgoing'
    
    def incoming_count(self, obj):
        return obj.incoming_flows.count()
    incoming_count.short_description = 'Incoming'


class TokenInline(admin.TabularInline):
    model = Token
    extra = 0
    fields = ['current_node', 'is_active', 'created_at', 'completed_at']
    readonly_fields = ['current_node', 'is_active', 'created_at', 'completed_at']
    can_delete = False


class TaskInstanceInline(admin.TabularInline):
    model = TaskInstance
    extra = 0
    fields = ['node', 'status', 'assignee', 'created_at', 'completed_at']
    readonly_fields = ['node', 'status', 'assignee', 'created_at', 'completed_at']
    can_delete = False


class ActivityLogInline(admin.TabularInline):
    model = ActivityLog
    extra = 0
    fields = ['timestamp', 'event_type', 'actor', 'node']
    readonly_fields = ['timestamp', 'event_type', 'actor', 'node']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ProcessInstance)
class ProcessInstanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'workflow', 'content_object_link', 'status', 'started_by', 'started_at', 'duration']
    list_filter = ['status', 'workflow', 'started_at']
    search_fields = ['id', 'started_by__username']
    readonly_fields = ['id', 'workflow', 'content_type', 'object_id', 'started_by', 'started_at', 'ended_at', 'updated_at', 'duration']
    
    fieldsets = [
        ('Process Information', {
            'fields': ['id', 'workflow', 'status']
        }),
        ('Business Object', {
            'fields': ['content_type', 'object_id']
        }),
        ('Variables', {
            'fields': ['variables']
        }),
        ('Timeline', {
            'fields': ['started_by', 'started_at', 'ended_at', 'duration', 'updated_at']
        }),
    ]
    
    inlines = [TokenInline, TaskInstanceInline, ActivityLogInline]
    
    def content_object_link(self, obj):
        if obj.content_object:
            return format_html('<a href="#">{}</a>', str(obj.content_object))
        return '-'
    content_object_link.short_description = 'Business Object'
    
    def duration(self, obj):
        if obj.ended_at and obj.started_at:
            delta = obj.ended_at - obj.started_at
            hours = delta.total_seconds() / 3600
            if hours < 1:
                return f"{delta.total_seconds() / 60:.0f} minutes"
            elif hours < 24:
                return f"{hours:.1f} hours"
            else:
                return f"{hours / 24:.1f} days"
        elif obj.started_at:
            return "In progress"
        return "-"
    duration.short_description = 'Duration'


@admin.register(TaskInstance)
class TaskInstanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'node_name', 'process_instance', 'status', 'assignee', 'created_at', 'completed_at']
    list_filter = ['status', 'node__node_type', 'created_at']
    search_fields = ['id', 'assignee__username', 'node__name']
    readonly_fields = ['id', 'process_instance', 'node', 'token', 'created_at', 'started_at', 'completed_at']
    
    fieldsets = [
        ('Task Information', {
            'fields': ['id', 'process_instance', 'node', 'token', 'status']
        }),
        ('Assignment', {
            'fields': ['assignee', 'candidate_users']
        }),
        ('Data', {
            'fields': ['input_data', 'output_data']
        }),
        ('Timeline', {
            'fields': ['created_at', 'started_at', 'completed_at', 'due_date']
        }),
    ]
    
    def node_name(self, obj):
        return obj.node.name
    node_name.short_description = 'Task'


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'event_type', 'process_instance', 'actor', 'node_name']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['process_instance__id', 'actor__username', 'node__name']
    readonly_fields = ['id', 'process_instance', 'task_instance', 'event_type', 'node', 'actor', 'details', 'timestamp']
    
    fieldsets = [
        ('Log Entry', {
            'fields': ['id', 'timestamp', 'event_type']
        }),
        ('Context', {
            'fields': ['process_instance', 'task_instance', 'node', 'actor']
        }),
        ('Details', {
            'fields': ['details']
        }),
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def node_name(self, obj):
        return obj.node.name if obj.node else '-'
    node_name.short_description = 'Node'


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'process_instance', 'current_node', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['process_instance__id', 'current_node__name']
    readonly_fields = ['id', 'process_instance', 'current_node', 'parent_token', 'created_at', 'completed_at']


@admin.register(SequenceFlow)
class SequenceFlowAdmin(admin.ModelAdmin):
    list_display = ['bpmn_id', 'name', 'workflow', 'source', 'target', 'has_condition']
    list_filter = ['workflow']
    search_fields = ['bpmn_id', 'name', 'source__name', 'target__name']
    readonly_fields = ['bpmn_id', 'created_at']
    
    def has_condition(self, obj):
        return bool(obj.condition_expression)
    has_condition.boolean = True
    has_condition.short_description = 'Conditional'
