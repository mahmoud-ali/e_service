from django.shortcuts import render
from django.core import serializers
from django.db.models import Prefetch
from django.http import JsonResponse,HttpResponse
from .models import STATE_CONFIRMED, GoldShippingForm
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def ShippingView(request):
    qs = GoldShippingForm.objects.filter(state=STATE_CONFIRMED).prefetch_related(Prefetch('goldshippingformalloy_set')) #.only('company_id','goldshippingformalloy__id') #updated_at
    qs_json = {'contents': 
        map(
            lambda obj: {
                'id':obj.id, 
                'company_id':obj.company_id,
                'date':obj.date,
                'form_no':obj.form_no,
                'state':obj.state,
                'details':
                        map(
                            lambda detail: {
                                'alloy_serial_no':detail.alloy_serial_no.alloy_serial_no,                        
                                'alloy_weight':detail.alloy_serial_no.alloy_weight,                        
                                'alloy_added_gold':detail.alloy_serial_no.alloy_added_gold,                        
                                'alloy_shipped':detail.alloy_serial_no.alloy_shipped,                        
                            },obj.goldshippingformalloy_set.all()
                        )
                },
                qs
            )
    } #serializers.serialize('json', qs)

    return Response( qs_json)