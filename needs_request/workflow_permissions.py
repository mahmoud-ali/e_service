"""
Workflow-based permissions for needs_request app.

This module provides permission functions that integrate with the BPMN workflow system.
"""

from bpmn_workflow.models import ProcessInstance, TaskInstance
from django.contrib.contenttypes.models import ContentType


def get_workflow_for_request(needs_request):
    """Helper to get workflow instance for a needs request"""
    return needs_request.get_workflow()


def has_workflow_read_permission(user, needs_request):
    """
    Check if user can read the needs request based on workflow state.
    
    Users can read if:
    - They are superuser
    - They created the request
    - They have a current task
    - They are in a group that previously acted on the workflow
    """
    if user.is_superuser:
        return True
    
    workflow = get_workflow_for_request(needs_request)
    if not workflow:
        # No workflow yet - use department-based permissions
        if user.groups.filter(name__in=['eom_pub', 'dga_pub']).exists():
            return True
        return False
    
    # Check if user started the process
    if workflow.started_by == user:
        return True
    
    # Check if user has any task (current or completed) in this workflow
    user_has_task = TaskInstance.objects.filter(
        process_instance=workflow,
        node__candidate_groups__overlap=list(user.groups.values_list('name', flat=True))
    ).exists()
    
    if user_has_task:
        return True
    
    # Operational employees can see all
    if user.groups.filter(name__in=[
        'sd_pub', 'doa_pub', 'it_pub', 'dgdhra_pub', 
        'dgfa_pub', 'agmfa_pub', 'gm_pub'
    ]).exists():
        return True
    
    return False


def has_workflow_action_permission(user, needs_request):
    """
    Check if user can perform actions on the needs request.
    
    User can act if they can complete any current task.
    """
    if user.is_superuser:
        return True
    
    current_tasks = needs_request.get_current_tasks()
    
    for task in current_tasks:
        if task.can_be_completed_by(user):
            return True
    
    return False


def get_user_current_task(user, needs_request):
    """
    Get the current task that the user can act on (if any).
    
    Returns:
        TaskInstance or None
    """
    current_tasks = needs_request.get_current_tasks()
    
    for task in current_tasks:
        if task.can_be_completed_by(user):
            return task
    
    return None


def can_user_perform_action(user, needs_request, action):
    """
    Check if user can perform a specific action.
    
    Args:
        user: User object
        needs_request: NeedsRequest object
        action: Action name (e.g., 'dga_approval', 'sd_comment')
        
    Returns:
        Boolean
    """
    if user.is_superuser:
        return True
    
    # Get user's current task
    task = get_user_current_task(user, needs_request)
    if not task:
        return False
    
    # Map actions to task types
    task_bpmn_id = task.node.bpmn_id
    
    action_mapping = {
        'dga_approval': 'Task_DGA_Approval',
        'dga_rejection': 'Task_DGA_Approval',
        'sd_comment': 'Task_SD_Comment',
        'doa_comment': 'Task_DOA_Comment',
        'it_comment': 'Task_IT_Comment',
        'dgdhra_recommendation': 'Task_DGDHRA_Recommendation',
        'dgfa_recommendation': 'Task_DGFA_Recommendation',
        'agmfa_approval': 'Task_AGMFA_Approval',
        'agmfa_rejection': 'Task_AGMFA_Approval',
        'gm_approval': 'Task_GM_Approval',
        'gm_rejection': 'Task_GM_Approval',
    }
    
    expected_task = action_mapping.get(action)
    return task_bpmn_id == expected_task
