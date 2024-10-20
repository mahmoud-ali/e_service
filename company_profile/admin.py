import codecs
import csv
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django import forms
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.messages import constants as message_constants
from import_export.admin import ExportActionMixin

from .models import AppCyanideCertificate, AppExplosivePermission, AppFuelPermission, AppFuelPermissionDetail, AppGoldProduction, AppGoldProductionDetail, AppHSEAccidentReport, AppHSEPerformanceReport, AppImportPermission, AppImportPermissionDetail, AppLocalPurchase, AppRenewalContract, AppRestartActivity, AppTemporaryExemption, AppWhomConcern, LkpAccidentType, LkpNationality,LkpState,LkpLocality,LkpMineral,LkpCompanyProductionStatus,LkpForeignerProcedureType,TblCompanyProduction, \
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

from .forms import AppCyanideCertificateAdminForm, AppExplosivePermissionAdminForm, AppFuelPermissionAdminForm, AppGoldProductionAdminForm, AppHSEAccidentReportAdminForm, AppHSEPerformanceReportAdminForm, AppImportPermissionAdminForm, AppLocalPurchaseAdminForm, AppRenewalContractAdminForm, AppRestartActivityAdminForm, AppTemporaryExemptionAdminForm, AppWhomConcernAdminForm, TblCompanyProductionForm,AppForignerMovementAdminForm,AppBorrowMaterialAdminForm,AppWorkPlanAdminForm, \
                   AppTechnicalFinancialReportAdminForm,AppChangeCompanyNameAdminForm, AppExplorationTimeAdminForm, \
                   AppAddAreaAdminForm,AppRemoveAreaAdminForm,AppTnazolShrakaAdminForm, AppTajeelTnazolAdminForm, \
                   AppTajmeedAdminForm,AppTakhaliAdminForm,AppTamdeedAdminForm,AppTaaweedAdminForm,AppMdaAdminForm, \
                   AppChangeWorkProcedureAdminForm,AppExportGoldAdminForm,AppExportGoldRawAdminForm,AppSendSamplesForAnalysisAdminForm, \
                   AppForeignerProcedureAdminForm,AppAifaaJomrkiAdminForm,AppReexportEquipmentsAdminForm, AppRequirementsListAdminForm, \
                   AppVisibityStudyAdminForm

from .workflow import SUBMITTED, get_state_choices,send_transition_email,ACCEPTED,APPROVED,REJECTED

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

    def has_add_permission(self, request, obj=None):
        return False
    
    def get_exclude(self,request, obj=None):
        fields = list(super().get_exclude(request, obj) or [])

        if not obj or obj.state == SUBMITTED:
            fields += ['reject_comments']
        
        return fields

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
        
        url = 'https://'+Site.objects.get_current().domain+'/app' #settings.BASE_URL
        
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
        
class LicenseCountFilter(admin.SimpleListFilter):
    title = _("license_count")    
    parameter_name = "license_count"
    def lookups(self, request, model_admin):
        return [
            ('0','0'),
            ('1','1'),
            ('2',_('more')),
        ]
    
    def queryset(self, request, queryset):
        facets = request.GET.get('_facets',False)

        if facets:
            return queryset
    
        qs = queryset.annotate(license_count=Count("tblcompanyproductionlicense"))
        val = self.value()
        if val == '0':
            return qs.filter(license_count=0)
        if val == '1':
            return qs.filter(license_count=1)
        if val == '2':
            return qs.filter(license_count__gt=1)
        
        return queryset

class TblCompanyProductionAdmin(ExportActionMixin,LoggingAdminMixin,admin.ModelAdmin):
    form = TblCompanyProductionForm
    fieldsets = [
        (None, {"fields": [("company_type","code"),("name_ar","name_en"),"nationality"]}),
        (_("Contact information"), {"fields": [("website","email"),("manager_name","manager_phone"),("rep_name","rep_phone"),"address"]}),
        (_("Company Status"), {"fields": ["status"]}),
     ]
     
    list_display = ["company_type","code","name_ar", "name_en", "status",'license_count','show_summary_link']
    list_filter = ["company_type","nationality","status","created_at",LicenseCountFilter]
    search_fields = ["code","name_ar","name_en"]
    exclude = ["created_at","created_by","updated_at","updated_by"]
    view_on_site = False

    @admin.display(description=_("license_count"))
    def license_count(self, obj):
        return obj.tblcompanyproductionlicense_set.count()

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

        email = obj.email

        if email and not TblCompanyProductionUserRole.objects.filter(company=obj,user__email=email).exists():
            #print("*****",obj,email)
            email = email.lower()
            User = get_user_model()     
            try:  
                com_user = User.objects.get(username=email)
            except:
                com_user = User.objects.create_user(email,email,settings.ACCOUNT_DEFAULT_PASSWORD)

            com_user.lang = 'ar'
            com_user.save()
            try: 
                u = TblCompanyProductionUserRole(company=obj,user=com_user)
                u.save()
            except:
                self.message_user(request,_('Email already exists!'),level=message_constants.ERROR)
        
    @admin.display(description=_('Show summary'))
    def show_summary_link(self, obj):
        url = reverse('profile:summary')
        return format_html('<a target="_blank" class="viewlink" href="{url}?id={id}">'+_('Show summary')+'</a>',
                    url=url,id=obj.id
                )

class TblCompanyProductionFactoryAdmin(LoggingAdminMixin,admin.ModelAdmin):
    fields = ["company", ("factory_type","capacity")]
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["company", "factory_type", "capacity"]    
    list_filter = ["factory_type"]
    view_on_site = False
    
# class ContractFileFilter(admin.SimpleListFilter):
#     title = _("include attachments")    
#     parameter_name = "include_attachments"
#     def lookups(self, request, model_admin):
#         return [
#             ('1',_('include attachments')),
#             ('2',_('not include attachments')),
#         ]
    
#     def queryset(self, request, queryset):
#         val = self.value()
#         if val == '1':
#             return queryset.exclude(contract_file='')
#         if val == '2':
#             return queryset.filter(contract_file='')
        
#         return queryset

class TblCompanyProductionLicenseAdmin(LoggingAdminMixin,admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["company",("license_no","license_count")]}),
        (_("General information"), {"fields": ["date",("start_date","end_date")]}),
        (_("Location information"), {"fields": [("state","locality","location","sheet_no")]}),
        (_("Contract information"), {"fields": ["mineral","area_initial","area","reserve","royalty","zakat","annual_rent","gov_rep","rep_percent","com_percent","business_profit","social_responsibility","contract_status","contract_file"]}),
     ]        
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["company","license_no", "start_date", "end_date","license_count","state","sheet_no","area_initial","area","contract_status","date","company_type"]        
    list_filter = ["company__company_type","state","mineral","contract_status",("contract_file",admin.EmptyFieldListFilter),"created_at"]
    search_fields = ["company__name_ar","company__name_en","sheet_no","license_no"]
    autocomplete_fields = ["company"]
    actions = ['export_as_csv']
    view_on_site = False

    formfield_overrides = {
        models.FloatField: {"widget": forms.TextInput},
        models.IntegerField: {"widget": forms.TextInput},
    }    

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

        qs = qs.filter(company__company_type__in=company_types)

        return qs

    class Media:
        js = ('admin/js/jquery.init.js','company_profile/js/lkp_state_change.js')

    @admin.display(description=_("company_type"))
    def company_type(self,obj):
        return _(obj.company.company_type)

    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="licenses.csv"'},
        )
        header = [
                    _("company"),_("License no"),_("start_date"),_("end_date"),_( "License count"),\
                    _("state"),_("sheet_no"),_("contract_status")
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for license in queryset.order_by("company"):

            row = [
                    license.company,license.license_no,license.start_date,license.end_date,license.license_count,license.state,\
                    license.sheet_no,license.contract_status
            ]
            writer.writerow(row)

        return response

admin.site.register(LkpNationality)
admin.site.register(LkpState)
# admin.site.register(LkpLocality)
admin.site.register(LkpMineral)
admin.site.register(LkpForeignerProcedureType)
admin.site.register(LkpCompanyProductionStatus) 
admin.site.register(TblCompanyProduction,TblCompanyProductionAdmin)
admin.site.register(LkpAccidentType) 

#admin.site.register(LkpCompanyProductionFactoryType)
admin.site.register(TblCompanyProductionFactory,TblCompanyProductionFactoryAdmin)

# admin.site.register(LkpCompanyProductionLicenseStatus)
admin.site.register(TblCompanyProductionLicense,TblCompanyProductionLicenseAdmin)

class TblCompanyProductionUserRoleAdmin( admin.ModelAdmin):
    
    list_display = ["company","user"]        
    list_filter = ["company","user"]
    
admin.site.register(TblCompanyProductionUserRole, TblCompanyProductionUserRoleAdmin)

class LkpLocalityAdmin( admin.ModelAdmin):
    model = LkpLocality
    exclude = ["id"]
    list_display = ["name","state"]        
    list_filter = ["state"]
    
admin.site.register(LkpLocality, LkpLocalityAdmin)

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
    
    list_display = ["company","lab_country","lab_city","lab_analysis_cost", "created_at", "created_by","updated_at", "updated_by"]        
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
    
    list_display = ["company","procedure_type","procedure_from","procedure_to", "created_at", "created_by","updated_at", "updated_by"]        
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
    
    list_display = ["company","license_type", "created_at", "created_by","updated_at", "updated_by"]        
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
    
    list_display = ["company","cause_for_equipments", "created_at", "created_by","updated_at", "updated_by"]        
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
    
    list_display = ["company","created_at", "created_by","updated_at", "updated_by"]        
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
    
    list_display = ["company","license_type", "created_at", "created_by","updated_at", "updated_by"]        
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

class AppImportPermissionDetailInline(admin.TabularInline):
    model = AppImportPermissionDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppImportPermissionAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppImportPermissionAdminForm
    inlines = [AppImportPermissionDetailInline]
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppImportPermission, AppImportPermissionAdmin)

class AppFuelPermissionDetailDetailInline(admin.TabularInline):
    model = AppFuelPermissionDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppFuelPermissionAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppFuelPermissionAdminForm
    inlines = [AppFuelPermissionDetailDetailInline]

    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppFuelPermission, AppFuelPermissionAdmin)

class AppHSEAccidentReportAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppHSEAccidentReportAdminForm
    
    list_display = ["company","accident_dt","accident_place","accident_type","accident_class", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppHSEAccidentReport, AppHSEAccidentReportAdmin)

class AppHSEPerformanceReportAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppHSEPerformanceReportAdminForm
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppHSEPerformanceReport, AppHSEPerformanceReportAdmin)

class AppWhomConcernAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppWhomConcernAdminForm
    
    list_display = ["company","whom_reason", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppWhomConcern, AppWhomConcernAdmin)

class AppGoldProductionDetailDetailInline(admin.TabularInline):
    model = AppGoldProductionDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppGoldProductionAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppGoldProductionAdminForm
    inlines = [AppGoldProductionDetailDetailInline]

    list_display = ["company","form_no", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppGoldProduction, AppGoldProductionAdmin)
