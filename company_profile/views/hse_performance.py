from django.forms import inlineformset_factory
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View, ListView, CreateView, DetailView
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from django.conf import settings

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site

from company_profile.utils import queryset_to_markdown

from ..models import AppHSEPerformanceReport, AppHSEPerformanceReportActivities, AppHSEPerformanceReportBillsOfQuantities, AppHSEPerformanceReportCadastralOperations, AppHSEPerformanceReportCadastralOperationsTwo, AppHSEPerformanceReportCatering, AppHSEPerformanceReportChemicalUsed, AppHSEPerformanceReportCyanideCNStorageSpecification, AppHSEPerformanceReportCyanideTable, AppHSEPerformanceReportDiseasesForWorkers, AppHSEPerformanceReportExplosivesUsed, AppHSEPerformanceReportExplosivesUsedSpecification, AppHSEPerformanceReportFireFighting, AppHSEPerformanceReportManPower, AppHSEPerformanceReportOilUsed, AppHSEPerformanceReportOtherChemicalUsed, AppHSEPerformanceReportProactiveIndicators, AppHSEPerformanceReportStatisticalData, AppHSEPerformanceReportTherapeuticUnit, AppHSEPerformanceReportWasteDisposal, AppHSEPerformanceReportWaterUsed, AppHSEPerformanceReportWorkEnvironment, TblCompany
from ..forms import AppHSEPerformanceReportForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppHSEPerformanceReportTable

from .application import ApplicationListView

model_details_lst = (
    AppHSEPerformanceReportManPower,
    AppHSEPerformanceReportFireFighting,
    AppHSEPerformanceReportWorkEnvironment,
    AppHSEPerformanceReportProactiveIndicators,
    AppHSEPerformanceReportActivities,
    AppHSEPerformanceReportChemicalUsed,
    AppHSEPerformanceReportOtherChemicalUsed,
    AppHSEPerformanceReportCyanideTable,
    AppHSEPerformanceReportCyanideCNStorageSpecification,
    AppHSEPerformanceReportWaterUsed,
    AppHSEPerformanceReportOilUsed,
    AppHSEPerformanceReportWasteDisposal,
    AppHSEPerformanceReportTherapeuticUnit,
    AppHSEPerformanceReportDiseasesForWorkers,
    AppHSEPerformanceReportStatisticalData,
    AppHSEPerformanceReportCatering,
)

explosive = (
    AppHSEPerformanceReportExplosivesUsed,
    AppHSEPerformanceReportExplosivesUsedSpecification,
    AppHSEPerformanceReportBillsOfQuantities,
    AppHSEPerformanceReportCadastralOperations,
    AppHSEPerformanceReportCadastralOperationsTwo,
)    


class AppHSEPerformanceReportListView(ApplicationListView):
    model = AppHSEPerformanceReport
    table_class = AppHSEPerformanceReportTable
    menu_name = "profile:app_hse_performance_list"
    title = _("List of HSE Performance Reports")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)


class AppHSEPerformanceReportCreateView(LoginRequiredMixin,View):
    model = AppHSEPerformanceReport
    model_details = model_details_lst
    form_class = AppHSEPerformanceReportForm
    detail_formset = None
    menu_name = "profile:app_hse_performance_list"
    title = _("Add new HSE Performance Report")
    template_name = "company_profile/views/hse_list_add_master_details.html"

    def dispatch(self, *args, **kwargs):           
        if self.request.user.pro_company.company.company_type in [TblCompany.COMPANY_TYPE_ENTAJ, TblCompany.COMPANY_TYPE_SAGEER, TblCompany.COMPANY_TYPE_EMTIAZ]:
            if explosive[0] not in self.model_details:
                self.model_details = self.model_details + explosive

        self.detail_formset = [inlineformset_factory(self.model, m, exclude=[],extra=0,can_delete=False,min_num=1, validate_min=True) for m in self.model_details]
            
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
            resp_user = get_sumitted_responsible('pro_company',self.object.company.company_type)
            url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
            send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
                
            return HttpResponseRedirect(self.success_url)            
        
        return render(request, self.template_name, self.extra_context)
        
class AppHSEPerformanceReportReadonlyView(LoginRequiredMixin,DetailView):
    model = AppHSEPerformanceReport
    model_details = model_details_lst
    form_class = AppHSEPerformanceReportForm
    detail_formset = None
    menu_name = "profile:app_hse_performance_list"
    title = _("Show HSE Performance Report")
    template_name = "company_profile/views/requirements_list_readonly_master_details.html"

    def dispatch(self, *args, **kwargs):
        if self.request.user.pro_company.company.company_type in [TblCompany.COMPANY_TYPE_ENTAJ, TblCompany.COMPANY_TYPE_SAGEER, TblCompany.COMPANY_TYPE_EMTIAZ]:
            if explosive[0] not in self.model_details:
                self.model_details = self.model_details + explosive

        self.detail_formset = [inlineformset_factory(self.model, m, exclude=[],extra=0,can_delete=False,min_num=1, validate_min=True) for m in self.model_details]
            
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

        return render(request, self.template_name, self.extra_context)
    
class AppHSEPerformanceReportAskAIView(LoginRequiredMixin,DetailView):
    model = AppHSEPerformanceReport
    model_details = model_details_lst
    template_name = "company_profile/views/ai_prompt.html"

    def get(self,request,pk):        
        obj = self.get_object()

        if obj.company.company_type in [TblCompany.COMPANY_TYPE_ENTAJ, TblCompany.COMPANY_TYPE_SAGEER, TblCompany.COMPANY_TYPE_EMTIAZ]:
            if explosive[0] not in self.model_details:
                self.model_details = self.model_details + explosive

        context = ""
        for model in self.model_details:
            qs = model.objects.filter(master=obj)
            if qs.count() > 0:
                context += "## "+qs[0]._meta.verbose_name
                context += queryset_to_markdown(qs,["id","master"]) + "\n\n"


        self.extra_context = {
            "prompt":"please analyze this HSE report for opertunity of improvements and suggest corrective actions",
            "context":context, 
         }

        return render(request, self.template_name, self.extra_context)
