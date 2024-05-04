from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View,ListView,CreateView
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from django.conf import settings

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.contrib.admin.widgets import AdminDateWidget

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from ..models import AppGoldProduction, AppGoldProductionDetail
from ..forms import AppGoldProductionForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppGoldProductionTable

from .application import ApplicationListView, ApplicationMasterDetailCreateView, ApplicationMasterDetailReadonlyView

class AppGoldProductionListView(ApplicationListView):
    model = AppGoldProduction
    table_class = AppGoldProductionTable
    menu_name = "profile:app_gold_production_list"
    title = _("List of Gold Productions")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)
    
class AppGoldProductionCreateView(LoginRequiredMixin,View):
    model = AppGoldProduction
    model_details = AppGoldProductionDetail
    model_details_fields = ["melt_dt","melt_bar_no","melt_bar_weight","melt_jaf","melt_khabath","melt_added_gold","melt_remaind"]
    form_class = AppGoldProductionForm
    detail_formset = None
    menu_name = "profile:app_gold_production_list"
    title = _("Add Gold Production")
    template_name = "company_profile/application_add_master_details.html"

    def dispatch(self, *args, **kwargs):       
        model_details_widgets = {
            "melt_dt": AdminDateWidget()
        }
        self.detail_formset = inlineformset_factory(self.model,self.model_details,widgets=model_details_widgets, fields=self.model_details_fields,extra=0,can_delete=False,min_num=1, validate_min=True)
            
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "detail_formset": self.detail_formset,
                            "detail_title":self.model_details._meta.verbose_name_plural,
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self,request):        
        return render(request, self.template_name, self.extra_context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,request.FILES)
        self.extra_context["form"] = form
        
        if form.is_valid():
            self.object = form.save(commit=False)
            
            self.object.company = request.user.pro_company.company
            self.object.created_by = self.object.updated_by = request.user
            self.object.attachement_file = self.request.FILES["attachement_file"]
        
            formset = self.detail_formset(request.POST,instance=self.object)
            self.extra_context["detail_formset"] = formset
            if formset.is_valid():
                self.object.save()
                formset.save()
                
                messages.add_message(request,messages.SUCCESS,_("Application sent successfully."))
                
                info = (self.object._meta.app_label, self.object._meta.model_name)
                resp_user = get_sumitted_responsible('pro_company')
                url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
                send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
                
                return HttpResponseRedirect(self.success_url)
            
        return render(request, self.template_name, self.extra_context)

class AppGoldProductionReadonlyView(ApplicationMasterDetailReadonlyView):
    model = AppGoldProduction
    model_details = AppGoldProductionDetail
    model_details_fields = ["melt_dt","melt_bar_no","melt_bar_weight","melt_jaf","melt_khabath","melt_added_gold","melt_remaind"]
    form_class = AppGoldProductionForm
    detail_formset = None
    menu_name = "profile:app_gold_production_list"
    title = _("Show Gold Production")