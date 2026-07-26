from django import template
from django.db import models

register = template.Library()

@register.filter(name="total_weight")
def total_weight(qs):
    # total = qs.aggregate(sum=models.Sum("gold_weight_in_gram"))['sum'] or 0
    total = 0
    for obj in qs:
        total += obj.appdabtiaatdetails_set.aggregate(sum=models.Sum("gold_weight_in_gram"))['sum'] or 0
    return round(total,2)

@register.filter(name="total_amount")
def total_amount(qs):
    total = 0
    for obj in qs:
        total += obj.koli_amount
    return round(total, 2)

