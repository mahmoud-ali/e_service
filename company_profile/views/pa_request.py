from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.conf import settings

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from pa.models import TblCompanyRequest
from pa.forms import TblCompanyRequestShowEditForm

from pa.tables import TblCompanyRequestCompanyTable

class AppRequestListView(LoginRequiredMixin,SingleTableView):
    model = TblCompanyRequest
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
        query = query.filter(commitement__company__id=self.request.user.pro_company.company.id)
        return query

class AppRequestReadonlyView(LoginRequiredMixin,SingleObjectMixin,View):
    model = TblCompanyRequest
    form_class = TblCompanyRequestShowEditForm
    menu_name = "profile:pa_request_list"
    title = _("Show added request")
    template_name = "company_profile/application_readonly.html"    

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))  

        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
         }
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(commitement__company__id=self.request.user.pro_company.company.id)

    def get(self,request,pk=0):     
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        self.extra_context["payment_state"] = TblCompanyRequest.REQUEST_PAYMENT_CHOICES[obj.payment_state]
        return render(request, self.template_name, self.extra_context)
