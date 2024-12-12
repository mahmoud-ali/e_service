from django import template

register = template.Library()

@register.filter(name="is_company_user")
def is_company_user(user):
    return user and user.is_authenticated and hasattr(user,"pro_company")

