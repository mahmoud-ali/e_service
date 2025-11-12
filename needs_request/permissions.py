
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import NeedsRequest

READ_PERMISSIONS = {
    'draft': ['eom_pub', 'dga_pub'],
    'dga_approval': ['eom_pub', 'dga_pub', 'sd_pub'],
    'dga_rejection': ['eom_pub', 'dga_pub'],
    'sd_comment': ['eom_pub', 'dga_pub', 'sd_pub', 'doa_pub'],
    'doa_comment': ['eom_pub', 'dga_pub', 'sd_pub', 'doa_pub', 'it_pub'],
    'it_comment': ['eom_pub', 'dga_pub', 'sd_pub', 'doa_pub', 'dgdhra_pub'],
    'dgdhra_recommendation': ['eom_pub', 'dga_pub', 'sd_pub', 'doa_pub', 'dgdhra_pub', 'dgfa_pub'],
    'dgfa_recommendation': ['eom_pub', 'dga_pub', 'sd_pub', 'doa_pub', 'dgdhra_pub', 'dgfa_pub', 'agmfa_pub'],
    'agmfa_approval': ['eom_pub', 'dga_pub', 'sd_pub', 'doa_pub', 'dgdhra_pub', 'dgfa_pub', 'agmfa_pub', 'gm_pub'],
    'agmfa_rejaction': ['eom_pub', 'dga_pub', 'sd_pub', 'doa_pub', 'dgdhra_pub', 'dgfa_pub', 'agmfa_pub'],
    'gm_approval': ['eom_pub', 'dga_pub', 'sd_pub', 'doa_pub', 'dgdhra_pub', 'dgfa_pub', 'agmfa_pub', 'gm_pub'],
    'gm_rejaction': ['eom_pub', 'dga_pub', 'sd_pub', 'doa_pub', 'dgdhra_pub', 'dgfa_pub', 'agmfa_pub', 'gm_pub'],
}

UPDATE_PERMISSIONS = {
    'draft': ['eom_pub', 'dga_pub'],
    'dga_approval': ['sd_pub'],
}

DELETE_PERMISSIONS = {
    'draft': ['eom_pub'],
}

# (status, group) -> allowed actions
ACTION_PERMISSIONS = {
    ('draft', 'dga_pub'): ['dga_approval', 'dga_rejection'],
    ('dga_approval', 'sd_pub'): ['sd_comment'],
    ('sd_comment', 'doa_pub'): ['doa_comment'],
    ('doa_comment', 'it_pub'): ['it_comment'],
    ('it_comment', 'dgdhra_pub'): ['dgdhra_recommendation'],
    ('dgdhra_recommendation', 'dgfa_pub'): ['dgfa_recommendation'],
    ('dgfa_recommendation', 'agmfa_pub'): ['agmfa_approval', 'agmfa_rejection'],
    ('agmfa_approval', 'gm_pub'): ['gm_approval', 'gm_rejection'],
}

def create_groups():
    """Create groups based on the permissions defined in this file."""
    group_names = set()
    for groups in READ_PERMISSIONS.values():
        group_names.update(groups)
    for groups in UPDATE_PERMISSIONS.values():
        group_names.update(groups)
    for groups in DELETE_PERMISSIONS.values():
        group_names.update(groups)
    for _, group in ACTION_PERMISSIONS.keys():
        group_names.add(group)

    for group_name in group_names:
        Group.objects.get_or_create(name=group_name)

def assign_model_permissions():
    """Assigns model-level permissions to groups."""
    try:
        eom_pub_group = Group.objects.get(name='eom_pub')
        content_type = ContentType.objects.get_for_model(NeedsRequest)
        add_needsrequest_permission = Permission.objects.get(content_type=content_type, codename='add_needsrequest')
        eom_pub_group.permissions.add(add_needsrequest_permission);
    except Group.DoesNotExist:
        print("Group 'eom_pub' does not exist. Please create it first.")
    except Permission.DoesNotExist:
        print("Permission 'add_needsrequest' does not exist. Please run migrations.")

def has_read_permission(user, needs_request):
    """Check read permission - uses workflow if available, falls back to old system"""
    if user.is_superuser:
        return True
    
    # Try workflow-based permission first
    workflow = needs_request.get_workflow()
    if workflow:
        from .workflow_permissions import has_workflow_read_permission
        return has_workflow_read_permission(user, needs_request)
    
    # Fall back to old approval_status based permissions
    user_groups = user.groups.values_list('name', flat=True)
    allowed_groups = READ_PERMISSIONS.get(needs_request.approval_status, [])
    
    return any(group in user_groups for group in allowed_groups)

def has_update_permission(user, needs_request):
    if user.is_superuser:
        return True
    
    user_groups = user.groups.values_list('name', flat=True)
    allowed_groups = UPDATE_PERMISSIONS.get(needs_request.approval_status, [])
    
    return any(group in user_groups for group in allowed_groups)

def has_delete_permission(user, needs_request):
    if user.is_superuser:
        return True
    
    user_groups = user.groups.values_list('name', flat=True)
    allowed_groups = DELETE_PERMISSIONS.get(needs_request.approval_status, [])
    
    return any(group in user_groups for group in allowed_groups)

def has_action_permission(user, needs_request, action):
    """Check action permission - uses workflow if available, falls back to old system"""
    if user.is_superuser:
        return True
    
    # Try workflow-based permission first
    workflow = needs_request.get_workflow()
    if workflow:
        from .workflow_permissions import can_user_perform_action
        return can_user_perform_action(user, needs_request, action)

    # Fall back to old approval_status based permissions
    user_groups = user.groups.values_list('name', flat=True)
    for group in user_groups:
        allowed_actions = ACTION_PERMISSIONS.get((needs_request.approval_status, group), [])
        if action in allowed_actions:
            return True
    return False

def is_operational_employee(user):
    if user.is_superuser:
        return True

    department_groups = ['sd_pub', 'doa_pub', 'dgdhra_pub', 'dgfa_pub', 'agmfa_pub', 'gm_pub']
    user_groups = user.groups.values_list('name', flat=True)

    return any(group in user_groups for group in department_groups)