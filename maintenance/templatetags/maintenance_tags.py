from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()

@register.filter(name='has_any_group')
def has_any_group(user, group_names_str):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    names = [n.strip() for n in group_names_str.split(',')]
    return user.groups.filter(name__in=names).exists()


_USER_NAME_CACHE = {}

@register.filter(name='user_display_name')
def user_display_name(user):
    if not user:
        return '—'
    if isinstance(user, str):
        return user
        
    cache_key = getattr(user, 'pk', str(user))
    if cache_key in _USER_NAME_CACHE:
        return _USER_NAME_CACHE[cache_key]

    full_name = ''
    if hasattr(user, 'get_full_name'):
        full_name = user.get_full_name()

    if full_name and '@' not in full_name and len(full_name.strip()) > 2:
        _USER_NAME_CACHE[cache_key] = full_name.strip()
        return full_name.strip()

    try:
        from hr.models import EmployeeBasic
        emp = None
        email = getattr(user, 'email', None)
        if email:
            emp = EmployeeBasic.objects.filter(email__iexact=email).first()
        if not emp and getattr(user, 'username', None):
            username = str(user.username)
            if username.isdigit():
                emp = EmployeeBasic.objects.filter(code=int(username)).first()
            elif '@' in username:
                code_part = username.split('@')[0].split('.')[-1]
                if code_part.isdigit():
                    emp = EmployeeBasic.objects.filter(code=int(code_part)).first()
        if emp and emp.name:
            _USER_NAME_CACHE[cache_key] = emp.name
            return emp.name
    except Exception:
        pass

    res = full_name.strip() if full_name else (getattr(user, 'username', '') or getattr(user, 'email', '') or str(user))
    # Only cache if it's a real name (not email/username fallback)
    if res and '@' not in res and res != getattr(user, 'username', '') and len(res) > 2:
        _USER_NAME_CACHE[cache_key] = res
    return res


@register.filter(name='translate_choice')
def translate_choice(key, labels_json):
    """يترجم مفاتيح الاختيارات الإنجليزية إلى نص عربي باستخدام قاموس JSON."""
    import json
    if not key:
        return key
    try:
        if isinstance(labels_json, str):
            labels = json.loads(labels_json)
        elif isinstance(labels_json, dict):
            labels = labels_json
        else:
            return key
        return labels.get(str(key), key)
    except (ValueError, TypeError):
        return key
