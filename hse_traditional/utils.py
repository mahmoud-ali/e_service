from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()
def get_user_emails_by_groups(group_names):
    """
    Retrieves email addresses of users belonging to specific groups.

    Args:
        group_names: A list of group names (strings).

    Returns:
        A list of email addresses (strings).  Returns an empty list if no
        users are found in the specified groups.
    """
    try:
        groups = Group.objects.filter(name__in=group_names)
        emails = User.objects.filter(groups__in=groups).values_list('email', flat=True)
        return list(emails)  # Convert QuerySet to a list
    except Group.DoesNotExist:
        return [] #Handles case when the group doesn't exist, and prevents crashing.
