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

from ..models import AppRenewalContract
from ..forms import AppRenewalContractForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppRenewalContractTable

from .application import ApplicationListView, ApplicationCreateView, ApplicationReadonlyView

class AppRenewalContractListView(ApplicationListView):
    model = AppRenewalContract
    table_class = AppRenewalContractTable
    menu_name = "profile:app_renewal_contract_list"
    title = _("List of Renewal Contracts")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)


class AppRenewalContractCreateView(ApplicationCreateView):
    model = AppRenewalContract
    form_class = AppRenewalContractForm
    menu_name = "profile:app_renewal_contract_list"
    title = _("Add Renewal Contract")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.company = self.request.user.pro_company.company
        self.object.created_by = self.object.updated_by = self.request.user

        self.object.attachement_file = self.request.FILES["attachement_file"]
        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Application sent successfully."))
        
        info = (self.object._meta.app_label, self.object._meta.model_name)
        resp_user = get_sumitted_responsible('pro_company',self.object.company.company_type)
        url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())
        
class AppRenewalContractReadonlyView(ApplicationReadonlyView):
    model = AppRenewalContract
    form_class = AppRenewalContractForm
    menu_name = "profile:app_renewal_contract_list"
    title = _("Show Renewal Contract")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))               
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(company=self.request.user.pro_company.company)

