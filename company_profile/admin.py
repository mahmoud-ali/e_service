from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django import forms
from django.contrib import admin
from django.contrib.sites.models import Site


from .models import AppCyanideCertificate, AppExplosivePermission, AppImportPermission, AppLocalPurchase, AppRenewalContract, AppRestartActivity, AppTemporaryExemption, LkpNationality,LkpState,LkpLocality,LkpMineral,LkpCompanyProductionStatus,LkpForeignerProcedureType,TblCompanyProduction, \
                                      LkpCompanyProductionFactoryType,TblCompanyProductionFactory,LkpCompanyProductionLicenseStatus, \
                                      TblCompanyProductionLicense,AppForignerMovement,TblCompanyProductionUserRole, \
                                      AppBorrowMaterial,AppBorrowMaterialDetail,AppWorkPlan,AppTechnicalFinancialReport, \
                                      AppChangeCompanyName, AppExplorationTime, AppAddArea,AppRemoveArea, AppTnazolShraka, \
                                      AppTajeelTnazol, AppTajmeed,AppTakhali,AppTamdeed,AppTaaweed,AppMda,AppChangeWorkProcedure, \
                                      AppExportGold,AppExportGoldRaw,AppSendSamplesForAnalysis,AppSendSamplesForAnalysisDetail, \
                                      AppForeignerProcedure,AppForeignerProcedureDetail,AppAifaaJomrki,AppAifaaJomrkiDetail, \
                                      AppReexportEquipments,AppReexportEquipmentsDetail,AppRequirementsList, \
                                      AppRequirementsListMangamEquipments,AppRequirementsListFactoryEquipments,AppRequirementsListElectricityEquipments, \
                                      AppRequirementsListChemicalLabEquipments,AppRequirementsListChemicalEquipments, \
                                      AppRequirementsListMotafjeratEquipments,AppRequirementsListVehiclesEquipments,TblCompany,AppVisibityStudy,AppVisibityStudyDetail

from .forms import AppCyanideCertificateAdminForm, AppExplosivePermissionAdminForm, AppImportPermissionAdminForm, AppLocalPurchaseAdminForm, AppRenewalContractAdminForm, AppRestartActivityAdminForm, AppTemporaryExemptionAdminForm, TblCompanyProductionForm,AppForignerMovementAdminForm,AppBorrowMaterialAdminForm,AppWorkPlanAdminForm, \
                   AppTechnicalFinancialReportAdminForm,AppChangeCompanyNameAdminForm, AppExplorationTimeAdminForm, \
                   AppAddAreaAdminForm,AppRemoveAreaAdminForm,AppTnazolShrakaAdminForm, AppTajeelTnazolAdminForm, \
                   AppTajmeedAdminForm,AppTakhaliAdminForm,AppTamdeedAdminForm,AppTaaweedAdminForm,AppMdaAdminForm, \
                   AppChangeWorkProcedureAdminForm,AppExportGoldAdminForm,AppExportGoldRawAdminForm,AppSendSamplesForAnalysisAdminForm, \
                   AppForeignerProcedureAdminForm,AppAifaaJomrkiAdminForm,AppReexportEquipmentsAdminForm, AppRequirementsListAdminForm, \
                   AppVisibityStudyAdminForm

from .workflow import get_state_choices,send_transition_email,ACCEPTED,APPROVED,REJECTED

admin.site.title = _("Site header")
admin.site.site_title = _("Site header")
admin.site.site_header = _("Site header")
admin.site.site_url = None
    
class LoggingAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class WorkflowAdminMixin:
    #list_select_related = True
    class Media:
        js = ('admin/js/jquery.init.js',"company_profile/js/state_control.js",)

    def has_change_permission(self, request, obj=None):
#        if obj and obj.state in[APPROVED,REJECTED]:
#            return False
#        
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        filter = []
        company_types = []

        if request.user.groups.filter(name="pro_company_application_accept").exists():
            filter += ["submitted"]
        if request.user.groups.filter(name="pro_company_application_approve").exists():
            filter += ["accepted","approved","rejected"]

        if request.user.groups.filter(name="company_type_entaj").exists():
            company_types += [TblCompany.COMPANY_TYPE_ENTAJ]
        if request.user.groups.filter(name="company_type_mokhalfat").exists():
            company_types += [TblCompany.COMPANY_TYPE_MOKHALFAT]
        if request.user.groups.filter(name="company_type_emtiaz").exists():
            company_types += [TblCompany.COMPANY_TYPE_EMTIAZ]
        if request.user.groups.filter(name="company_type_sageer").exists():
            company_types += [TblCompany.COMPANY_TYPE_SAGEER]


        qs = qs.filter(state__in=filter)
        qs = qs.filter(company__company_type__in=company_types)

        return qs

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

        user= None
        email = None
        lang = None
        
        url = 'https://'+Site.objects.get_current().domain #settings.BASE_URL
        
        if obj.notify:
            # print("next transition*****",obj.state)
            if obj.state in (ACCEPTED,APPROVED,REJECTED):
                email = obj.company.email
                lang = get_user_model().objects.get(email=email).lang
                url += obj.get_absolute_url()
            else:
                email = request.user.email
                lang = get_user_model().objects.get(email=email).lang
                url += request.path
                                
            send_transition_email(obj.state,email,url,lang.lower())
            obj.notify = False
            obj.save()
        

class TblCompanyProductionAdmin(LoggingAdminMixin,admin.ModelAdmin):
    form = TblCompanyProductionForm
    fieldsets = [
        (None, {"fields": [("company_type"),("name_ar","name_en"),"nationality"]}),
        (_("Location information"), {"fields": [("state","locality"),"location","cordinates","address",("website","email")]}),
        (_("Contact information"), {"fields": [("manager_name","manager_phone"),("rep_name","rep_phone")]}),
        (_("Company Status"), {"fields": ["status"]}),
     ]
     
    list_display = ["name_ar", "name_en", "state","status"]
    list_filter = ["name_ar","name_en","state"]
         
    exclude = ["created_at","created_by","updated_at","updated_by"]
    view_on_site = False

    class Media:
        js = ('admin/js/jquery.init.js','company_profile/js/lkp_state_change.js')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        company_types = []

        if request.user.groups.filter(name="company_type_entaj").exists():
            company_types += [TblCompany.COMPANY_TYPE_ENTAJ]
        if request.user.groups.filter(name="company_type_mokhalfat").exists():
            company_types += [TblCompany.COMPANY_TYPE_MOKHALFAT]
        if request.user.groups.filter(name="company_type_emtiaz").exists():
            company_types += [TblCompany.COMPANY_TYPE_EMTIAZ]
        if request.user.groups.filter(name="company_type_sageer").exists():
            company_types += [TblCompany.COMPANY_TYPE_SAGEER]

        qs = qs.filter(company_type__in=company_types)

        return qs

    
    def get_form(self, request, *args, **kwargs):
        form = super(TblCompanyProductionAdmin, self).get_form(request, *args, **kwargs)
        company_type = []
        if request.user.groups.filter(name="company_type_entaj").exists():
            company_type += [(TblCompany.COMPANY_TYPE_ENTAJ,_(TblCompany.COMPANY_TYPE_ENTAJ))]
        if request.user.groups.filter(name="company_type_mokhalfat").exists():
            company_type += [(TblCompany.COMPANY_TYPE_MOKHALFAT,_(TblCompany.COMPANY_TYPE_MOKHALFAT))]
        if request.user.groups.filter(name="company_type_emtiaz").exists():
            company_type += [(TblCompany.COMPANY_TYPE_EMTIAZ,_(TblCompany.COMPANY_TYPE_EMTIAZ))]
        if request.user.groups.filter(name="company_type_sageer").exists():
            company_type += [(TblCompany.COMPANY_TYPE_SAGEER,_(TblCompany.COMPANY_TYPE_SAGEER))]

        form.choices = company_type
        return form
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)                

        if not obj.id:
            User = get_user_model()            
            com_user = User.objects.create_user(obj.name_en,obj.email,settings.ACCOUNT_DEFAULT_PASSWORD)
            u = TblCompanyProductionUserRole(company=obj,user=com_user)
            u.save()
        
class TblCompanyProductionFactoryAdmin(LoggingAdminMixin,admin.ModelAdmin):
    fields = ["company", ("factory_type","capacity")]
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["company", "factory_type", "capacity"]    
    list_filter = ["factory_type"]
    view_on_site = False
    
class TblCompanyProductionLicenseAdmin(LoggingAdminMixin,admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["company"]}),
        (_("General information"), {"fields": ["date",("start_date","end_date"),("sheet_no","cordinates")]}),
        (_("Contract information"), {"fields": ["area","reserve","gov_rep","rep_percent","com_percent","royalty","zakat","annual_rent","contract_status","contract_file"]}),
     ]        
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["company","sheet_no","date", "start_date", "end_date"]        
    list_filter = ["date","sheet_no"]
    view_on_site = False
     
admin.site.register(LkpNationality)
admin.site.register(LkpState)
admin.site.register(LkpLocality)
admin.site.register(LkpMineral)
admin.site.register(LkpForeignerProcedureType)
#admin.site.register(LkpCompanyProductionStatus) 
admin.site.register(TblCompanyProduction,TblCompanyProductionAdmin)

#admin.site.register(LkpCompanyProductionFactoryType)
admin.site.register(TblCompanyProductionFactory,TblCompanyProductionFactoryAdmin)

#admin.site.register(LkpCompanyProductionLicenseStatus)
admin.site.register(TblCompanyProductionLicense,TblCompanyProductionLicenseAdmin)

class TblCompanyProductionUserRoleAdmin( admin.ModelAdmin):
    
    list_display = ["company","user"]        
    list_filter = ["company","user"]
    
admin.site.register(TblCompanyProductionUserRole, TblCompanyProductionUserRoleAdmin)

class AppForignerMovementAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppForignerMovementAdminForm
    
    list_display = ["company","period_from","period_to", "nationality", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppForignerMovement, AppForignerMovementAdmin)

class AppBorrowMaterialDetailInline(admin.TabularInline):
    model = AppBorrowMaterialDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppBorrowMaterialAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppBorrowMaterialAdminForm
    inlines = [AppBorrowMaterialDetailInline]     
    
    list_display = ["company","company_from","borrow_date", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["borrow_date"]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)                
            
admin.site.register(AppBorrowMaterial, AppBorrowMaterialAdmin)

class AppWorkPlanAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppWorkPlanAdminForm
    
    list_display = ["company","plan_from","plan_to", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppWorkPlan, AppWorkPlanAdmin)

class AppTechnicalFinancialReportAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppTechnicalFinancialReportAdminForm
    
    list_display = ["company","report_from","report_to","report_type", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppTechnicalFinancialReport, AppTechnicalFinancialReportAdmin)

class AppChangeCompanyNameAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppChangeCompanyNameAdminForm
    
    list_display = ["company","new_name", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppChangeCompanyName, AppChangeCompanyNameAdmin)

class AppExplorationTimeAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppExplorationTimeAdminForm
    
    list_display = ["company","expo_from","expo_to", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppExplorationTime, AppExplorationTimeAdmin)

class AppAddAreaAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppAddAreaAdminForm
    
    list_display = ["company","area_in_km2", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppAddArea, AppAddAreaAdmin)

class AppRemoveAreaAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppRemoveAreaAdminForm
    
    list_display = ["company","remove_type","area_in_km2","area_percent_from_total", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppRemoveArea, AppRemoveAreaAdmin)

class AppTnazolShrakaAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppTnazolShrakaAdminForm
    
    list_display = ["company","tnazol_type","tnazol_for", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppTnazolShraka, AppTnazolShrakaAdmin)

class AppTajeelTnazolAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppTajeelTnazolAdminForm
    
    list_display = ["company","tnazol_type", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppTajeelTnazol, AppTajeelTnazolAdmin)

class AppTajmeedAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppTajmeedAdminForm
    
    list_display = ["company","tajmeed_from","tajmeed_to", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppTajmeed, AppTajmeedAdmin)

class AppTakhaliAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppTakhaliAdminForm
    
    list_display = ["company","technical_presentation_date", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppTakhali, AppTakhaliAdmin)

class AppTamdeedAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppTamdeedAdminForm
    
    list_display = ["company","tamdeed_from","tamdeed_to", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppTamdeed, AppTamdeedAdmin)

class AppTaaweedAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppTaaweedAdminForm
    
    list_display = ["company","taaweed_from","taaweed_to", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppTaaweed, AppTaaweedAdmin)

class AppMdaAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppMdaAdminForm
    
    list_display = ["company","mda_from","mda_to", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppMda, AppMdaAdmin)

class AppChangeWorkProcedureAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppChangeWorkProcedureAdminForm
    
    list_display = ["company","reason_for_change","purpose_for_change","rational_reason", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppChangeWorkProcedure, AppChangeWorkProcedureAdmin)

class AppExportGoldAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppExportGoldAdminForm
    
    list_display = ["company","total_in_gram","net_in_gram","zakat_in_gram", "awaad_jalila_in_gram","arbah_amal_in_gram","sold_for_bank_of_sudan_in_gram", "amount_to_export_in_gram","remain_in_gram", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppExportGold, AppExportGoldAdmin)

class AppExportGoldRawAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppExportGoldRawAdminForm
    
    list_display = ["mineral","license_type","amount_in_gram","sale_price","export_country","export_city", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppExportGoldRaw, AppExportGoldRawAdmin)

class AppSendSamplesForAnalysisDetailInline(admin.TabularInline):
    model = AppSendSamplesForAnalysisDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppSendSamplesForAnalysisAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppSendSamplesForAnalysisAdminForm
    inlines = [AppSendSamplesForAnalysisDetailInline]
    
    list_display = ["lab_country","lab_city","lab_analysis_cost", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppSendSamplesForAnalysis, AppSendSamplesForAnalysisAdmin)

class AppForeignerProcedureDetailInline(admin.TabularInline):
    model = AppForeignerProcedureDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppForeignerProcedureAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppForeignerProcedureAdminForm
    inlines = [AppForeignerProcedureDetailInline]
    
    list_display = ["procedure_type","procedure_from","procedure_to", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppForeignerProcedure, AppForeignerProcedureAdmin)

class AppAifaaJomrkiDetailInline(admin.TabularInline):
    model = AppAifaaJomrkiDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppAifaaJomrkiAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppAifaaJomrkiAdminForm
    inlines = [AppAifaaJomrkiDetailInline]
    
    list_display = ["license_type", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppAifaaJomrki, AppAifaaJomrkiAdmin)

class AppReexportEquipmentsDetailInline(admin.TabularInline):
    model = AppReexportEquipmentsDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppReexportEquipmentsAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppReexportEquipmentsAdminForm
    inlines = [AppReexportEquipmentsDetailInline]
    
    list_display = ["cause_for_equipments", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppReexportEquipments, AppReexportEquipmentsAdmin)

class AppRequirementsListMangamEquipmentsInline(admin.TabularInline):
    model = AppRequirementsListMangamEquipments
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppRequirementsListFactoryEquipmentsInline(admin.TabularInline):
    model = AppRequirementsListFactoryEquipments
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppRequirementsListElectricityEquipmentsInline(admin.TabularInline):
    model = AppRequirementsListElectricityEquipments
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppRequirementsListChemicalLabEquipmentsInline(admin.TabularInline):
    model = AppRequirementsListChemicalLabEquipments
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppRequirementsListChemicalEquipmentsInline(admin.TabularInline):
    model = AppRequirementsListChemicalEquipments
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppRequirementsListMotafjeratEquipmentsInline(admin.TabularInline):
    model = AppRequirementsListMotafjeratEquipments
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppRequirementsListVehiclesEquipmentsInline(admin.TabularInline):
    model = AppRequirementsListVehiclesEquipments
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppRequirementsListAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppRequirementsListAdminForm
    inlines = [AppRequirementsListMangamEquipmentsInline,AppRequirementsListFactoryEquipmentsInline, AppRequirementsListElectricityEquipmentsInline,  AppRequirementsListChemicalLabEquipmentsInline,AppRequirementsListChemicalEquipmentsInline, AppRequirementsListMotafjeratEquipmentsInline,AppRequirementsListVehiclesEquipmentsInline]
    
    list_display = ["created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppRequirementsList, AppRequirementsListAdmin)

class AppVisibityStudyDetailInline(admin.TabularInline):
    model = AppVisibityStudyDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppVisibityStudyAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppVisibityStudyAdminForm
    inlines = [AppVisibityStudyDetailInline]
    
    list_display = ["license_type", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False

admin.site.register(AppVisibityStudy, AppVisibityStudyAdmin)

class AppTemporaryExemptionAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppTemporaryExemptionAdminForm
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppTemporaryExemption, AppTemporaryExemptionAdmin)

class AppLocalPurchaseAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppLocalPurchaseAdminForm
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppLocalPurchase, AppLocalPurchaseAdmin)

class AppCyanideCertificateAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppCyanideCertificateAdminForm
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppCyanideCertificate, AppCyanideCertificateAdmin)

class AppExplosivePermissionAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppExplosivePermissionAdminForm
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppExplosivePermission, AppExplosivePermissionAdmin)

class AppRestartActivityAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppRestartActivityAdminForm
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppRestartActivity, AppRestartActivityAdmin)

class AppRenewalContractAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppRenewalContractAdminForm
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppRenewalContract, AppRenewalContractAdmin)

class AppImportPermissionAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppImportPermissionAdminForm
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppImportPermission, AppImportPermissionAdmin)
