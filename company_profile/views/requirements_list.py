from django.urls import reverse_lazy
from django.views.generic import View,ListView,CreateView,DetailView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from django.conf import settings
from django.forms import inlineformset_factory

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from ..models import AppRequirementsList,AppRequirementsListMangamEquipments,AppRequirementsListFactoryEquipments, \
                     AppRequirementsListElectricityEquipments, AppRequirementsListChemicalLabEquipments, \
                     AppRequirementsListChemicalEquipments, AppRequirementsListMotafjeratEquipments,AppRequirementsListVehiclesEquipments
from ..forms import AppRequirementsListForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppRequirementsListTable

from .application import ApplicationListView, ApplicationCreateView, ApplicationReadonlyView, \
                         ApplicationMasterDetailCreateView, ApplicationMasterDetailReadonlyView


class AppRequirementsListListView(ApplicationListView):
    model = AppRequirementsList
    table_class = AppRequirementsListTable
    menu_name = "profile:app_requirements_list_list"
    title = _("List of Requirements List")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)

class AppRequirementsListCreateView(LoginRequiredMixin,View):
    model = AppRequirementsList
    model_details = [AppRequirementsListMangamEquipments,AppRequirementsListFactoryEquipments, AppRequirementsListElectricityEquipments,   AppRequirementsListChemicalLabEquipments, AppRequirementsListChemicalEquipments, AppRequirementsListMotafjeratEquipments,AppRequirementsListVehiclesEquipments]
    model_details_fields = ["item","description","qty"]
    form_class = AppRequirementsListForm
    detail_formset = None
    menu_name = "profile:app_requirements_list_list"
    title = _("Add Requirements List")
    template_name = "company_profile/views/requirements_list_add_master_details.html"

    def dispatch(self, *args, **kwargs):         
        self.detail_formset = [inlineformset_factory(self.model, m, fields=self.model_details_fields,extra=0,can_delete=False,min_num=1, validate_min=True) for m in self.model_details]
            
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "detail_formset": self.detail_formset,
                            "detail_title":[m._meta.verbose_name_plural for m in self.model_details],
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
            
            self.extra_context["detail_formset"] = [formset(request.POST,instance=self.object) for formset in self.detail_formset]
            for formset in self.extra_context["detail_formset"]:
                if not formset.is_valid():
                    return render(request, self.template_name, self.extra_context)

            self.object.save()
            for formset in self.extra_context["detail_formset"]:
                formset.save()
                
            messages.add_message(request,messages.SUCCESS,_("Application sent successfully."))
                
            info = (self.object._meta.app_label, self.object._meta.model_name)
            resp_user = get_sumitted_responsible('pro_company')
            url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
            send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
                
            return HttpResponseRedirect(self.success_url)            

class AppRequirementsListReadonlyView(LoginRequiredMixin,DetailView):
    model = AppRequirementsList
    model_details = [AppRequirementsListMangamEquipments,AppRequirementsListFactoryEquipments, AppRequirementsListElectricityEquipments,   AppRequirementsListChemicalLabEquipments, AppRequirementsListChemicalEquipments, AppRequirementsListMotafjeratEquipments,AppRequirementsListVehiclesEquipments]
    model_details_fields = ["item","description","qty"]
    form_class = AppRequirementsListForm
    detail_formset = None
    menu_name = "profile:app_requirements_list_list"
    title = _("Show Requirements List")
    template_name = "company_profile/views/requirements_list_readonly_master_details.html"
        
    def dispatch(self, *args, **kwargs):
        self.detail_formset = [inlineformset_factory(self.model, m, fields=self.model_details_fields,extra=0,can_delete=False,min_num=1, validate_min=True) for m in self.model_details]
            
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "detail_formset": self.detail_formset,
                            "detail_title":[m._meta.verbose_name_plural for m in self.model_details],
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self,request,pk=0):        
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["detail_formset"] = [formset(instance=obj) for formset in self.detail_formset]
        #print("88888888",self.extra_context["detail_title"])
        return render(request, self.template_name, self.extra_context)

