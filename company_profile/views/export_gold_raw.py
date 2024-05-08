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

from ..models import AppExportGoldRaw
from ..forms import AppExportGoldRawForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppExportGoldRawTable

from .application import ApplicationListView, ApplicationCreateView, ApplicationReadonlyView

class AppExportGoldRawListView(ApplicationListView):
    model = AppExportGoldRaw
    table_class = AppExportGoldRawTable
    menu_name = "profile:app_export_gold_raw_list"
    title = _("List of export gold raw")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)


class AppExportGoldRawCreateView(ApplicationCreateView):
    model = AppExportGoldRaw
    form_class = AppExportGoldRawForm
    menu_name = "profile:app_export_gold_raw_list"
    title = _("Add export gold raw")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.company = self.request.user.pro_company.company
        self.object.created_by = self.object.updated_by = self.request.user

        self.object.f11 = self.request.FILES["f11"]
        self.object.f12 = self.request.FILES["f12"]
        self.object.f13 = self.request.FILES["f13"]
        self.object.f14 = self.request.FILES["f14"]
        self.object.f15 = self.request.FILES["f15"]
        self.object.f16 = self.request.FILES["f16"]
        self.object.f17 = self.request.FILES["f17"]
        self.object.f18 = self.request.FILES["f18"]
        self.object.f19 = self.request.FILES["f19"]
        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Application sent successfully."))
        
        info = (self.object._meta.app_label, self.object._meta.model_name)
        resp_user = get_sumitted_responsible('pro_company',self.object.company.company_type)
        url = 'https://'+Site.objects.get_current().domain+'/app'+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())
        
class AppExportGoldRawReadonlyView(ApplicationReadonlyView):
    model = AppExportGoldRaw
    form_class = AppExportGoldRawForm
    menu_name = "profile:app_export_gold_raw_list"
    title = _("Show export gold raw")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))               
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(company=self.request.user.pro_company.company)

