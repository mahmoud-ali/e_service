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
    # total = qs.aggregate(sum=models.Sum("kolli"))['sum'] or 0
    
    total = 0
    for obj in qs:
        qs2 = obj.appdabtiaatdetails_set.annotate(
            total=models.F('gold_weight_in_gram') * models.F('gold_price') *0.22
        )
        total += qs2.aggregate(sum=models.Sum("total"))['sum'] or 0
    return round(total,2)
