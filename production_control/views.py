from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from django.views.generic import TemplateView

from django.contrib.auth import authenticate

from .models import STATE_CONFIRMED, GoldProductionForm, GoldShippingForm
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class UserPermissionMixin(UserPassesTestMixin):
    user_groups = []

    def test_func(self):
        id = int(self.request.GET['id'])
        qs = self.model.objects.filter(pk=id)
        
        if not qs:
            return False
            
        if self.request.user.is_superuser:
            return qs.exists()

        if self.request.user.groups.filter(name__in=("production_control_sector_mgr",)).exists():
            try:
                company_type = self.request.user.gold_production_sector_user.company_type
                sector = self.request.user.gold_production_sector_user.sector
                return qs.filter(
                    company__company_type__in= [company_type],
                    license__state__sector=sector
                ).exists()
            except Exception as e:
                print(e)

        if self.request.user.groups.filter(name__in=("production_control_state_mgr",)).exists():
            try:
                company_type = self.request.user.gold_production_state_user.company_type
                states = self.request.user.gold_production_state_user.state.values_list('id',flat=True)

                return qs.filter(
                    company__company_type__in= [company_type],
                    license__state__in=states
                ).exists()
            except Exception as e:
                print(e)
        
        try:
            license_lst = self.request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('license',flat=True)
            return qs.filter(license__id__in=license_lst).exists()
        except Exception as e:
            print(e)

        return False
    
class CertificateTemplate(LoginRequiredMixin,UserPermissionMixin,TemplateView):
    def _partition(self,lst, size=20):
        l = len(lst)
        if l <= 18:
            yield lst
        else:
            yield lst[0 : 18]
            for i in range(18, l, size):
                yield lst[i : i+size]

class ProductionCert(CertificateTemplate):
    template_name = 'production_control/production_form.html'
    model = GoldProductionForm

    def get(self,*args,**kwargs):
        id = int(self.request.GET['id'])
        obj = get_object_or_404(self.model,pk=id)
        license = {"state":"","locality":""}
        if obj.license:
            license = obj.license

        alloy_chunks = self._partition(obj.goldproductionformalloy_set.all())

        self.extra_context = {
            'object': obj,
            'alloy_chunks': alloy_chunks,
            'license':license, 
            # 'state_repr': state_repr,
        }
        return render(self.request, self.template_name, self.extra_context)    

class ShippingCert(CertificateTemplate):
    template_name = 'production_control/shipping_form.html'
    model = GoldShippingForm

    def get(self,*args,**kwargs):
        id = int(self.request.GET['id'])
        obj = get_object_or_404(self.model,pk=id)
        license = {"state":"","locality":""}
        if obj.license:
            license = obj.license

        alloy_chunks = self._partition(obj.goldshippingformalloy_set.all())

        self.extra_context = {
            'object': obj,
            'alloy_chunks': alloy_chunks,
            'license':license, 
            # 'state_repr': state_repr,
        }
        return render(self.request, self.template_name, self.extra_context)    

@api_view(['GET'])
# @authentication_classes([TokenAuthentication,])
# @permission_classes([IsAuthenticated])
def ProductionView(request,from_dt,to_dt):
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

    # try:
    #     from_dt = request.query_params.get('from') # datetime.datetime.strptime(request.GET['from'] ,'%Y/%m/%d')
    #     to_dt =  request.query_params.get('to') #datetime.datetime.strptime(request.GET['to'],'%Y/%m/%d')
    # except:
    #     from_dt = '1900-01-01'
    #     to_dt = '1900-01-01'

    qs = GoldProductionForm.objects.filter(state=GoldProductionForm.STATE_APPROVED,date__gte=from_dt,date__lte=to_dt).prefetch_related(Prefetch('goldproductionformalloy_set')) #.only('company_id','goldshippingformalloy__id') #updated_at
    qs_json = {'contents': 
        map(
            get_data,
                qs
            )
    }

    return Response( qs_json)

@api_view(['GET'])
# @authentication_classes([TokenAuthentication,])
# @permission_classes([IsAuthenticated])
def ShippingView(request,from_dt,to_dt):
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

    # try:
    #     from_dt = request.GET['from'] # datetime.datetime.strptime(request.GET['from'] ,'%Y/%m/%d')
    #     to_dt =  request.GET['to'] #datetime.datetime.strptime(request.GET['to'],'%Y/%m/%d')
    # except:
    #     from_dt = '1900-01-01'
    #     to_dt = '1900-01-01'

    qs = GoldShippingForm.objects.filter(state=GoldShippingForm.STATE_APPROVED,date__gte=from_dt,date__lte=to_dt).prefetch_related(Prefetch('goldshippingformalloy_set')) #.only('company_id','goldshippingformalloy__id') #updated_at
    qs_json = {'contents': 
        map(
            get_data,
                qs
            )
    }

    return Response( qs_json)