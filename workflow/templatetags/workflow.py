from django import template
from django.db import models

register = template.Library()

@register.filter(name="get_next_states")
def get_next_states(obj,user):
    return getattr(obj,'get_next_states')(user)
