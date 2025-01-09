import datetime
from django.shortcuts import render
from django.core import serializers
from django.db.models import Prefetch
from django.http import JsonResponse,HttpResponse

from django.contrib.auth import authenticate

from .models import STATE_CONFIRMED, GoldProductionForm, GoldShippingForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.authtoken.models import Token

# @api_view(['GET'])
# def auth(request):
#     username = request.data.get('username','')
#     password = request.data.get('password','')

#     status = 403
#     token_key = ''

#     user = authenticate(email=username, password=password)

#     if user is not None and user.groups.filter(name__in=("pro_company_application_accept",)).exists():
#         token,created = Token.objects.get_or_create(user=user)
#         status = 200
#         token_key = token

#     return Response( 
#         data={
#             'status':200,
#             'token':token_key,
#         },
#         status=status
#     )

@api_view(['GET'])
def ProductionView(request):
    def get_data(obj):
        try:
            moragib = obj.created_by.moragib_list.name
        except:
            moragib = ''

        return {'id':obj.id, 
            'company_id':obj.company_id,
            'date':obj.date,
            'form_no':obj.form_no,
            'alloy_khabath':obj.alloy_khabath,
            'alloy_remaind':obj.alloy_remaind,
            'moragib':moragib,
            'details':
                    map(
                        lambda detail: {
                            'id':detail.id,                        
                            'alloy_serial_no':detail.alloy_serial_no,                        
                            'alloy_weight':detail.alloy_weight,                        
                            'alloy_added_gold':detail.alloy_added_gold,                        
                        },obj.goldproductionformalloy_set.all()
                    )
            }

    try:
        from_dt = request.GET['from'] # datetime.datetime.strptime(request.GET['from'] ,'%Y/%m/%d')
        to_dt =  request.GET['to'] #datetime.datetime.strptime(request.GET['to'],'%Y/%m/%d')
    except:
        from_dt = '1900-01-01'
        to_dt = '1900-01-01'

    qs = GoldProductionForm.objects.filter(state=STATE_CONFIRMED,date__gte=from_dt,date__lte=to_dt).prefetch_related(Prefetch('goldproductionformalloy_set')) #.only('company_id','goldshippingformalloy__id') #updated_at
    qs_json = {'contents': 
        map(
            get_data,
                qs
            )
    }

    return Response( qs_json)

@api_view(['GET'])
def ShippingView(request):
    def get_data(obj):
        try:
            moragib = obj.created_by.moragib_list.name
        except:
            moragib = ''

        return {
                'id':obj.id, 
                'company_id':obj.company_id,
                'date':obj.date,
                'form_no':obj.form_no,
                'moragib':moragib,
                'details':
                        map(
                            lambda detail: {
                                'production_id':detail.alloy_serial_no.master.id,                        
                                'alloy_serial_no':detail.alloy_serial_no.alloy_serial_no,                        
                                'alloy_weight':detail.alloy_serial_no.alloy_weight,                        
                                'alloy_added_gold':detail.alloy_serial_no.alloy_added_gold,                        
                            },obj.goldshippingformalloy_set.all()
                        )
            }

    try:
        from_dt = request.GET['from'] # datetime.datetime.strptime(request.GET['from'] ,'%Y/%m/%d')
        to_dt =  request.GET['to'] #datetime.datetime.strptime(request.GET['to'],'%Y/%m/%d')
    except:
        from_dt = '1900-01-01'
        to_dt = '1900-01-01'

    qs = GoldShippingForm.objects.filter(state=STATE_CONFIRMED,date__gte=from_dt,date__lte=to_dt).prefetch_related(Prefetch('goldshippingformalloy_set')) #.only('company_id','goldshippingformalloy__id') #updated_at
    qs_json = {'contents': 
        map(
            get_data,
                qs
            )
    }

    return Response( qs_json)