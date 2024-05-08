from django.urls import reverse_lazy
from django.views.generic import View,ListView,CreateView
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from django.conf import settings

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from ..models import AppRemoveArea
from ..forms import AppRemoveAreaForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppRemoveAreaTable

from .application import ApplicationListView, ApplicationCreateView, ApplicationReadonlyView

class AppRemoveAreaListView(ApplicationListView):
    model = AppRemoveArea
    table_class = AppRemoveAreaTable
    menu_name = "profile:app_remove_area_list"
    title = _("List of removed area")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)


class AppRemoveAreaCreateView(ApplicationCreateView):
    model = AppRemoveArea
    form_class = AppRemoveAreaForm
    menu_name = "profile:app_remove_area_list"
    title = _("Add remove area application")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.company = self.request.user.pro_company.company
        self.object.created_by = self.object.updated_by = self.request.user

        self.object.geo_coordinator_for_removed_area_file = self.request.FILES["geo_coordinator_for_removed_area_file"]
        self.object.geo_coordinator_for_remain_area_file = self.request.FILES["geo_coordinator_for_remain_area_file"]
        self.object.map_for_clarification_file = self.request.FILES["map_for_clarification_file"]
        self.object.technical_report_for_removed_area_file = self.request.FILES["technical_report_for_removed_area_file"]
        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Application sent successfully."))
        
        info = (self.object._meta.app_label, self.object._meta.model_name)
        resp_user = get_sumitted_responsible('pro_company',self.object.company.company_type)
        url = 'https://'+Site.objects.get_current().domain+'/app'+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())
        
class AppRemoveAreaReadonlyView(ApplicationReadonlyView):
    model = AppRemoveArea
    form_class = AppRemoveAreaForm
    menu_name = "profile:app_remove_area_list"
    title = _("Show removed area")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))               
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(company=self.request.user.pro_company.company)

