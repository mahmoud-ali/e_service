from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def has_field(model_class, field_name: str) -> bool:
    try:
        model_class._meta.get_field(field_name)
        return True
    except:
        return False
    
@register.simple_tag
def show_notification_count(request,app,admin_model):
    if not admin_model or app.get('app_label') != 'company_profile':
        return f"{admin_model.get('name')}"
    
    filter = []
    
    if request.user.groups.filter(name__in=["pro_company_application_accept",]).exists():
        filter += ["submitted","review_accept"]
    if request.user.groups.filter(name__in=["pro_company_application_approve",]).exists():
        filter += ["accepted"]

    Model = admin_model.get('model')
    # print("************",Model)
    try:
        if has_field(Model,"state"):
            count = Model.objects.filter(state__in=filter).count()
            if count:
                return mark_safe(f'{admin_model.get('name')} (<span style="color:#afa38d">{count}</span>)')
    except:
        pass

    return f"{admin_model.get('name')}"
