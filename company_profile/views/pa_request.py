from django.forms import inlineformset_factory
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from django.conf import settings

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

from django.contrib.sites.models import Site

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from pa.models import TblCompanyRequestDetail, TblCompanyRequestMaster,TblCompanyPaymentMaster
from pa.forms import TblCompanyRequestShowEditForm

from pa.tables import TblCompanyRequestCompanyTable

class AppRequestListView(LoginRequiredMixin,SingleTableView):
    model = TblCompanyRequestMaster
    table_class = TblCompanyRequestCompanyTable
    menu_name = "profile:pa_request_list"
    title = _("List of requests")
    context_object_name = "apps"    
    template_name = "company_profile/application_list.html"     
    paginator_class = LazyPaginator
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        self.extra_context = {
                            "type":kwargs.get("type",1),
                            "menu_name":self.menu_name,
                            "title":self.title,
         }
        
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        if not hasattr(self.request.user,'pro_company'):
            query = query.none()
        else:
            query = query.filter(commitment__company__id=self.request.user.pro_company.company.id)
        return query
    
    def get(self,request,*args, **kwargs):  
        response = super().get(request,*args, **kwargs)

        if not request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME):
            translation.activate(request.user.lang)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME,request.user.lang)

        return response

# class AppRequestReadonlyView(LoginRequiredMixin,SingleObjectMixin,View):
#     model = TblCompanyRequestMaster
#     model_details = TblCompanyPaymentMaster
#     model_details_fields = ["request","payment_dt","amount","currency","exchange_rate"]
#     form_class = TblCompanyRequestShowEditForm
#     menu_name = "profile:pa_request_list"
#     title = _("Show added request")
#     template_name = "company_profile/application_readonly_master_details.html"    

#     def dispatch(self, *args, **kwargs):         
#         if not hasattr(self.request.user,"pro_company"):
#             return HttpResponseRedirect(reverse_lazy("profile:home"))  

#         self.detail_formset = inlineformset_factory(self.model, self.model_details, fields=self.model_details_fields,extra=0,can_delete=False)

#         self.extra_context = {
#                             "menu_name":self.menu_name,
#                             "title":self.title, 
#                             "detail_formset": self.detail_formset,
#                             "detail_title":self.model_details._meta.verbose_name_plural,
#          }
#         return super().dispatch(*args, **kwargs)        

#     def get_queryset(self):
#         query = super().get_queryset()        
#         return query.filter(commitement__company__id=self.request.user.pro_company.company.id)

#     def get(self,request,pk=0):     
#         obj = self.get_object()
#         self.extra_context["form"] = self.form_class(instance=obj)
#         self.extra_context["object"] = obj
#         self.extra_context["detail_formset"] = self.detail_formset(instance=obj)
#         self.extra_context["payment_state"] = TblCompanyRequestMaster.REQUEST_PAYMENT_CHOICES[obj.payment_state]
        
#         return render(request, self.template_name, self.extra_context)

model_master = TblCompanyRequestMaster
details = [
        {
            "id":1,
            "title":"تفاصيل المطالبة",
            "args":[
                model_master,
                TblCompanyRequestDetail
            ],
            "kwargs":{
               "fields":['item','amount'],
                "extra":0,
                "can_delete":False,
                "min_num":1, 
                "validate_min":True
            },
        },
    ]
class ApplicationReadonlyView(LoginRequiredMixin,UserPassesTestMixin,SingleObjectMixin,View):
    model = None
    form_class = None
    details = []
    success_url = None
    title = None    
    user_groups = ['pa_data_entry','pa_manager']
    menu_name = ""  
    template_name = "pa/application_readonly_master_details.html"
    
    def test_func(self):
        return hasattr(self.request.user,'pro_company')

    def dispatch(self, *args, **kwargs):         
        self.details_formset = []
        for d in self.details:
            if d['kwargs'].get('can_delete'):
                d['kwargs']['can_delete'] = False
            self.details_formset.append({
                "title":d['title'],
                "formset":inlineformset_factory(*d['args'], **d['kwargs']),
            })
            
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "menu_edit_name":self.menu_name,
                            "menu_delete_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "details": self.details_formset,
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        for detail in self.details_formset:
            formset = detail['formset'](instance=obj)
            detail['formset'] = formset
        return render(request, self.template_name, self.extra_context)


class AppRequestReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = TblCompanyRequestShowEditForm
    details = details
    menu_name = "profile:pa_request_list"
    menu_edit_name = None
    menu_delete_name = None
    title = _("Show added request")
    template_name = "company_profile/application_readonly_master_details2.html"    

    def get_queryset(self):
        query = super().get_queryset()        
        if not hasattr(self.request.user,'pro_company'):
            query = query.none()
        else:
            query = query.filter(commitment__company__id=self.request.user.pro_company.company.id)
        return query
