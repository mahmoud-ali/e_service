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

from ..models import AppExportGold
from ..forms import AppExportGoldForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppExportGoldTable

from .application import ApplicationListView, ApplicationCreateView, ApplicationReadonlyView

class AppExportGoldListView(ApplicationListView):
    model = AppExportGold
    table_class = AppExportGoldTable
    menu_name = "profile:app_export_gold_list"
    title = _("List of export gold")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)


class AppExportGoldCreateView(ApplicationCreateView):
    model = AppExportGold
    form_class = AppExportGoldForm
    menu_name = "profile:app_export_gold_list"
    title = _("Add export gold")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.company = self.request.user.pro_company.company
        self.object.created_by = self.object.updated_by = self.request.user

        self.object.f1 = self.request.FILES.get("f1",'')
        self.object.f2 = self.request.FILES.get("f2",'')
        self.object.f3 = self.request.FILES.get("f3",'')
        self.object.f4 = self.request.FILES.get("f4",'')
        self.object.f5 = self.request.FILES.get("f5",'')
        self.object.f6 = self.request.FILES.get("f6",'')
        self.object.f7 = self.request.FILES.get("f7",'')
        self.object.f8 = self.request.FILES.get("f8",'')
        self.object.f9 = self.request.FILES.get("f9",'')
        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Application sent successfully."))
        
        info = (self.object._meta.app_label, self.object._meta.model_name)
        resp_user = get_sumitted_responsible('pro_company',self.object.company.company_type)
        url = 'https://'+Site.objects.get_current().domain+'/app'+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())
        
class AppExportGoldReadonlyView(ApplicationReadonlyView):
    model = AppExportGold
    form_class = AppExportGoldForm
    menu_name = "profile:app_export_gold_list"
    title = _("Show export gold")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))               
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(company=self.request.user.pro_company.company)

