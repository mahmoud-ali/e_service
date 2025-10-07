from django import template

register = template.Library()

SHOW_NOTIFICATIONS = [
    'employeetelegramfamily',
    'employeetelegrammoahil',
    'employeetelegrambankaccount',
    'employeetelegramregistration',
]

@register.filter(name='has_any_group')
def has_any_group(user, group_names):
    group_list = group_names.split(',')
    return user.groups.filter(name__in=group_list).exists()

@register.filter(name="show_draft_count")
def show_draft_count(admin_model):
    if not admin_model or admin_model.get('object_name').lower() not in SHOW_NOTIFICATIONS:
        return ''
    count = admin_model.get('model').objects.filter(state=1).count()
    return f"({count})" if count else ''
