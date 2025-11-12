"""
Workflow utility functions for needs_request app.

Helper functions to work with BPMN workflows.
"""

from django.contrib.contenttypes.models import ContentType
from bpmn_workflow.engine import BPMNEngine
from bpmn_workflow.models import ProcessInstance, TaskInstance


def start_needs_request_workflow(needs_request, user):
    """
    Start the approval workflow for a needs request.
    
    Args:
        needs_request: NeedsRequest instance
        user: User who is starting the workflow
        
    Returns:
        ProcessInstance object
    """
    return BPMNEngine.start_process(
        workflow_key='needs_request_approval',
        business_object=needs_request,
        user=user,
        initial_variables={
            'department': needs_request.department.name,
            'date': needs_request.date.isoformat(),
        }
    )


def complete_current_task(needs_request, user, action_data):
    """
    Complete the current workflow task for a needs request.
    
    Args:
        needs_request: NeedsRequest instance
        user: User completing the task
        action_data: Dict with form data
        
    Returns:
        True if task was completed, False otherwise
    """
    # Get current task for this user
    current_tasks = needs_request.get_current_tasks()
    
    for task in current_tasks:
        if task.can_be_completed_by(user):
            BPMNEngine.complete_task(
                task_instance=task,
                user=user,
                data=action_data
            )
            return True
    
    return False


def get_workflow_summary(needs_request):
    """
    Get a summary of the workflow state.
    
    Returns:
        Dict with workflow information
    """
    workflow = needs_request.get_workflow()
    
    if not workflow:
        return {
            'exists': False,
            'status': 'No workflow',
            'current_step': None,
            'can_act': False,
        }
    
    current_tasks = list(workflow.get_current_tasks())
    current_task = current_tasks[0] if current_tasks else None
    
    return {
        'exists': True,
        'status': workflow.status,
        'started_at': workflow.started_at,
        'started_by': workflow.started_by,
        'current_step': current_task.node.name if current_task else 'Completed',
        'current_step_bpmn_id': current_task.node.bpmn_id if current_task else None,
        'total_tasks': workflow.tasks.count(),
        'completed_tasks': workflow.tasks.filter(status='completed').count(),
    }


def get_task_statistics(needs_request):
    """
    Get statistics about task completion times.
    
    Returns:
        List of dicts with task information
    """
    workflow = needs_request.get_workflow()
    if not workflow:
        return []
    
    stats = []
    for task in workflow.tasks.all().select_related('node'):
        duration = None
        if task.completed_at and task.created_at:
            delta = task.completed_at - task.created_at
            duration = delta.total_seconds() / 3600  # hours
        
        stats.append({
            'task_name': task.node.name,
            'status': task.status,
            'assignee': task.assignee.username if task.assignee else 'Unassigned',
            'created_at': task.created_at,
            'completed_at': task.completed_at,
            'duration_hours': duration,
        })
    
    return stats


def can_restart_workflow(needs_request, user):
    """
    Check if workflow can be restarted (for rejected or cancelled requests).
    
    Args:
        needs_request: NeedsRequest instance
        user: User attempting to restart
        
    Returns:
        Boolean
    """
    if not user.is_superuser and not user.groups.filter(name='eom_pub').exists():
        return False
    
    workflow = needs_request.get_workflow()
    if not workflow:
        return False
    
    return workflow.status in ['terminated', 'suspended']
