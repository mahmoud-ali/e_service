from django import template
from django.db import models

register = template.Library()

@register.filter(name="total_alloy_weight")
def total_alloy_weight(qs):
    qs = qs.prefetch_related(models.Prefetch("appmovegolddetails_set"))
    # print("qs",)
    total = qs.aggregate(sum=models.Sum("appmovegolddetails__alloy_weight_in_gram"))['sum'] or 0
    # total = 0
    # for obj in qs:
    #     total += obj.appmovegolddetails_set.aggregate(sum=models.Sum("alloy_weight_in_gram"))['sum'] or 0
    return round(total,2)

@register.filter(name="total_alloy_count")
def total_alloy_count(qs):
    qs = qs.prefetch_related(models.Prefetch("appmovegolddetails_set"))
    total = qs.aggregate(count=models.Count("appmovegolddetails"))['count'] or 0
    
    # total = 0
    # for obj in qs:
    #     total += obj.appmovegolddetails_set.count()
    return round(total,2)
