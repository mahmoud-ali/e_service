from django.urls import reverse_lazy
from django.views.generic import View,TemplateView,ListView,DetailView,CreateView,UpdateView,DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404,render
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from django.conf import settings

from django.forms import inlineformset_factory

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from company_profile.utils import get_app_metrics

from ..models import LkpState,LkpLocality,TblCompanyProduction,AppForignerMovement,AppBorrowMaterial,AppBorrowMaterialDetail
from ..forms import LanguageForm,AppForignerMovementForm,AppBorrowMaterialForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppForignerMovementTable,AppBorrowMaterialTable

from .application import ApplicationListView, ApplicationCreateView, ApplicationReadonlyView, \
                         ApplicationMasterDetailCreateView, ApplicationMasterDetailReadonlyView, TranslationMixin
from .work_plan import AppWorkPlanListView,AppWorkPlanCreateView,AppWorkPlanReadonlyView
from .technical_financial_report import AppTechnicalFinancialReportListView, AppTechnicalFinancialReportCreateView, AppTechnicalFinancialReportReadonlyView
from .change_company_name import AppChangeCompanyNameListView, AppChangeCompanyNameCreateView, AppChangeCompanyNameReadonlyView
from .exploration_time import AppExplorationTimeListView, AppExplorationTimeCreateView, AppExplorationTimeReadonlyView
from .add_area import AppAddAreaListView, AppAddAreaCreateView, AppAddAreaReadonlyView
from .remove_area import AppRemoveAreaListView, AppRemoveAreaCreateView, AppRemoveAreaReadonlyView
from .tnazol_shraka import AppTnazolShrakaListView, AppTnazolShrakaCreateView, AppTnazolShrakaReadonlyView
from .tajeel_tnazol import AppTajeelTnazolListView, AppTajeelTnazolCreateView, AppTajeelTnazolReadonlyView
from .tajmeed import AppTajmeedListView, AppTajmeedCreateView, AppTajmeedReadonlyView
from .takhali import AppTakhaliListView, AppTakhaliCreateView, AppTakhaliReadonlyView
from .tamdeed import AppTamdeedListView, AppTamdeedCreateView, AppTamdeedReadonlyView
from .taaweed import AppTaaweedListView, AppTaaweedCreateView, AppTaaweedReadonlyView
from .mda import AppMdaListView, AppMdaCreateView, AppMdaReadonlyView
from .change_work_procedure import AppChangeWorkProcedureListView, AppChangeWorkProcedureCreateView, AppChangeWorkProcedureReadonlyView
from .export_gold import AppExportGoldListView, AppExportGoldCreateView, AppExportGoldReadonlyView
from .export_gold_raw import AppExportGoldRawListView, AppExportGoldRawCreateView, AppExportGoldRawReadonlyView
from .send_samples_for_analysis import AppSendSamplesForAnalysisListView, AppSendSamplesForAnalysisCreateView, AppSendSamplesForAnalysisReadonlyView
from .foreigner_procedure import AppForeignerProcedureListView, AppForeignerProcedureCreateView, AppForeignerProcedureReadonlyView
from .aifaa_jomrki import AppAifaaJomrkiListView, AppAifaaJomrkiCreateView, AppAifaaJomrkiReadonlyView
from .reexport_equipments import AppReexportEquipmentsListView, AppReexportEquipmentsCreateView, AppReexportEquipmentsReadonlyView
from .requirements_list import AppRequirementsListListView, AppRequirementsListCreateView, AppRequirementsListReadonlyView
from .visibilty_study import AppVisibityStudyListView, AppVisibityStudyCreateView, AppVisibityStudyReadonlyView
from .temporary_exemption import AppTemporaryExemptionListView,AppTemporaryExemptionCreateView,AppTemporaryExemptionReadonlyView
from .local_purchase import AppLocalPurchaseListView,AppLocalPurchaseCreateView,AppLocalPurchaseReadonlyView
from .cyanide_certificate import AppCyanideCertificateListView,AppCyanideCertificateCreateView,AppCyanideCertificateReadonlyView
from .explosive_permission import AppExplosivePermissionListView,AppExplosivePermissionCreateView,AppExplosivePermissionReadonlyView
from .restart_activity import AppRestartActivityListView,AppRestartActivityCreateView,AppRestartActivityReadonlyView
from .renewal_contract import AppRenewalContractListView,AppRenewalContractCreateView,AppRenewalContractReadonlyView
from .import_permission import AppImportPermissionListView,AppImportPermissionCreateView,AppImportPermissionReadonlyView
from .fuel_permission import AppFuelPermissionListView,AppFuelPermissionCreateView,AppFuelPermissionReadonlyView
from .hse_accident import AppHSEAccidentReportListView,AppHSEAccidentReportCreateView,AppHSEAccidentReportReadonlyView
from .hse_performance import AppHSEPerformanceReportListView,AppHSEPerformanceReportCreateView,AppHSEPerformanceReportReadonlyView
from .whom_concern import AppWhomConcernListView,AppWhomConcernCreateView,AppWhomConcernReadonlyView
from .gold_production import AppGoldProductionListView,AppGoldProductionCreateView,AppGoldProductionReadonlyView
from .pa_request import AppRequestListView,AppRequestReadonlyView

class SetLanguageView(LoginRequiredMixin,View):
    def post(self,request):
        form = LanguageForm(request.POST)
        
        if form.is_valid():
            user_language = request.POST['language']

            request.user.lang= user_language
            request.user.save()

            translation.activate(user_language)
            response = HttpResponseRedirect(reverse_lazy("profile:home"))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)        
            return response
        return HttpResponseBadRequest()
               
class LkpSelectView(LoginRequiredMixin,TemplateView):
    template_name = 'company_profile/select.html'
    kwargs = None

    def get_queryset(self):
        return None #not implemented

    def dispatch(self, *args, **kwargs):
        self.kwargs = kwargs
        self.extra_context = {
                            "options":self.get_queryset(), 
                            "old_value":self.kwargs['dependent_id']
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self, request, *args, **kwargs):                   
        return render(request, self.template_name, self.extra_context)    

class CompanySummaryView(LoginRequiredMixin,TemplateView):
    template_name = 'company_profile/summary.html'
    kwargs = None


    def get(self, request, *args, **kwargs):    
        id = request.GET.get("id",None)
        company = get_object_or_404(TblCompanyProduction,pk=id)
        self.extra_context = {
            "company": company,
            "licenses": company.tblcompanyproductionlicense_set.all()
        }
        return render(request, self.template_name, self.extra_context)    

class HomePageView(LoginRequiredMixin,TranslationMixin,TemplateView):
    template_name = 'company_profile/home.html'
    menu_name = 'profile:home'

    def _get_filter(self,filter_dict={}):
        if self.request.user.is_superuser:
            return filter_dict
        
        return filter_dict.update({'company__id':self.request.user.pro_company.company.id})

    def dispatch(self, *args, **kwargs): 
        is_admin = self.request.user.is_superuser
        if is_admin or hasattr(self.request.user,'pro_company'):
            in_progress_qs = get_app_metrics( \
                ['id','company','created_at','updated_at'], #fields
                self._get_filter({'state__in':[SUBMITTED,ACCEPTED]}), #,'company__id':self.request.user.pro_company.company.id}, #filter
                ['company'], #select_related
                ["-created_at"] #order_by
            )[:10]
    
            accepted_qs = get_app_metrics( \
                ['id','company','created_at','updated_at'], #fields
                self._get_filter({'state__in':[APPROVED]}), #{'state__in':[APPROVED],'company__id':self.request.user.pro_company.company.id}, #filter
                ['company'], #select_related
                ["-created_at"] #order_by
            )[:10]

            rejected_qs = get_app_metrics( \
                ['id','company','created_at','updated_at'], #fields
                self._get_filter({'state__in':[REJECTED]}), #{'state__in':[REJECTED],'company__id':self.request.user.pro_company.company.id}, #filter
                ['company'], #select_related
                ["-created_at"] #order_by
            )[:10]

            self.extra_context = {
                "accepted_progress":accepted_qs,
                "rejected_progress":rejected_qs,
                "in_progress":in_progress_qs,
                "menu_name":self.menu_name,
            }
        return super().dispatch(*args, **kwargs)    

class LkpLocalitySelectView(LkpSelectView):
    def get_queryset(self):
        qs = LkpLocality.objects.filter(state__id = self.kwargs['master_id'])
        return qs
    
class AppForignerMovementListView(ApplicationListView):
    model = AppForignerMovement
    table_class = AppForignerMovementTable
    menu_name = "profile:app_foreigner_list"
    title = _("List of foreigner movements")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)


class AppForignerMovementCreateView(ApplicationCreateView):
    model = AppForignerMovement
    form_class = AppForignerMovementForm
    menu_name = "profile:app_foreigner_list"
    title = _("Add new movement")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.company = self.request.user.pro_company.company
        self.object.created_by = self.object.updated_by = self.request.user
        self.object.official_letter_file = self.request.FILES["official_letter_file"]
        self.object.passport_copy_file = self.request.FILES["passport_copy_file"]
        self.object.cv_file = self.request.FILES["cv_file"]
        self.object.experiance_certificates_file = self.request.FILES["experiance_certificates_file"]
        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Application sent successfully."))
        
        info = (self.object._meta.app_label, self.object._meta.model_name)
        resp_user = get_sumitted_responsible('pro_company',self.object.company.company_type)
        url = 'https://'+Site.objects.get_current().domain+'/app'+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())
        
class AppForignerMovementReadonlyView(ApplicationReadonlyView):
    model = AppForignerMovement
    form_class = AppForignerMovementForm
    menu_name = "profile:app_foreigner_list"
    title = _("Show movement")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))               
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(company=self.request.user.pro_company.company)
        
class AppBorrowMaterialListView(ApplicationListView):
    model = AppBorrowMaterial
    table_class = AppBorrowMaterialTable
    menu_name = "profile:app_borrow_list"
    title = _("List of borrow materials")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)                    
    
    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id) #.only(*self.table_class.Meta.fields)

class AppBorrowMaterialCreateView(ApplicationMasterDetailCreateView):
    model = AppBorrowMaterial
    model_details = AppBorrowMaterialDetail
    model_details_fields = ["material","quantity"]
    form_class = AppBorrowMaterialForm
    detail_formset = None
    menu_name = "profile:app_borrow_list"
    title = _("Add new borrow materials")
    template_name = "company_profile/application_add_master_details.html"

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,request.FILES)
        self.extra_context["form"] = form
        
        if form.is_valid():
            self.object = form.save(commit=False)
            
            self.object.company = request.user.pro_company.company
            self.object.created_by = self.object.updated_by = request.user
            self.object.borrow_materials_list_file = self.request.FILES["borrow_materials_list_file"]
            self.object.borrow_from_approval_file = self.request.FILES["borrow_from_approval_file"]
            
        
            formset = self.detail_formset(request.POST,instance=self.object)
            self.extra_context["detail_formset"] = formset
            if formset.is_valid():
                self.object.save()
                formset.save()
                
                messages.add_message(request,messages.SUCCESS,_("Application sent successfully."))
                
                info = (self.object._meta.app_label, self.object._meta.model_name)
                resp_user = get_sumitted_responsible('pro_company',self.object.company.company_type)
                url = 'https://'+Site.objects.get_current().domain+'/app'+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
                send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
                
                return HttpResponseRedirect(self.success_url)
            
        return render(request, self.template_name, self.extra_context)
            
class AppBorrowMaterialReadonlyView(ApplicationMasterDetailReadonlyView):
    model = AppBorrowMaterial
    model_details = AppBorrowMaterialDetail
    model_details_fields = ["material","quantity"]
    form_class = AppBorrowMaterialForm
    detail_formset = None
    menu_name = "profile:app_borrow_list"
    title = _("Show borrow materials")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))               
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(company=self.request.user.pro_company.company)

