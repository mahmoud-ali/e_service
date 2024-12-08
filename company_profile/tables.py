from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from .models import AppCyanideCertificate, AppExplosivePermission, AppForignerMovement,AppBorrowMaterial, AppFuelPermission, AppGoldProduction, AppHSEAccidentReport, AppHSEPerformanceReport, AppImportPermission, AppLocalPurchase, AppRenewalContract, AppRestartActivity, AppTemporaryExemption, AppWhomConcern,AppWorkPlan,AppTechnicalFinancialReport,AppChangeCompanyName, \
                    AppExplorationTime, AppAddArea,AppRemoveArea,AppTnazolShraka,AppTajeelTnazol,AppTajmeed,AppTakhali, \
                    AppTamdeed, AppTaaweed, AppMda,AppChangeWorkProcedure,AppExportGold,AppExportGoldRaw, \
                    AppSendSamplesForAnalysis,AppForeignerProcedure,AppAifaaJomrki,AppReexportEquipments,AppRequirementsList, \
                    AppVisibityStudy

class AppTable(tables.Table):
    menu_name = None
    relation_fields = []

class AppForignerMovementTable(AppTable):
    menu_name = "profile:app_foreigner_show"
    relation_fields = ["nationality"]

    class Meta:
        model = AppForignerMovement
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","route_from","route_to","period_from","period_to","address_in_sudan","nationality","passport_no")
        empty_text = _("No records.")        

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)
        
class AppBorrowMaterialTable(AppTable):
    menu_name = "profile:app_borrow_show"
    relation_fields = ["company_from"]

    class Meta:
        model = AppBorrowMaterial
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","company_from_str","borrow_date")        
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)
        
class AppWorkPlanTable(AppTable):
    menu_name = "profile:app_work_plan_show"
    relation_fields = []

    class Meta:
        model = AppWorkPlan
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","plan_from","plan_to")        
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppTechnicalFinancialReportTable(AppTable):
    menu_name = "profile:app_technical_financial_report_show"
    relation_fields = []

    class Meta:
        model = AppTechnicalFinancialReport
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","report_from","report_to","report_type")        
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppChangeCompanyNameTable(AppTable):
    menu_name = "profile:app_change_company_name_show"
    relation_fields = []

    class Meta:
        model = AppChangeCompanyName
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","new_name")        
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppExplorationTimeTable(AppTable):
    menu_name = "profile:app_exploration_time_show"
    relation_fields = []

    class Meta:
        model = AppExplorationTime
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","expo_from","expo_to")        
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppAddAreaTable(AppTable):
    menu_name = "profile:app_add_area_show"
    relation_fields = []

    class Meta:
        model = AppAddArea
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","area_in_km2")        
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppRemoveAreaTable(AppTable):
    menu_name = "profile:app_remove_area_show"
    relation_fields = []

    class Meta:
        model = AppRemoveArea
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","remove_type","area_in_km2","area_percent_from_total")        
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppTnazolShrakaTable(AppTable):
    menu_name = "profile:app_tnazol_shraka_show"
    relation_fields = []

    class Meta:
        model = AppTnazolShraka
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","tnazol_type","tnazol_for")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppTajeelTnazolTable(AppTable):
    menu_name = "profile:app_tajeel_tnazol_show"
    relation_fields = []

    class Meta:
        model = AppTajeelTnazol
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","tnazol_type")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppTajmeedTable(AppTable):
    menu_name = "profile:app_tajeel_tnazol_show"
    relation_fields = []

    class Meta:
        model = AppTajmeed
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","tajmeed_from","tajmeed_to")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppTakhaliTable(AppTable):
    menu_name = "profile:app_takhali_show"
    relation_fields = []

    class Meta:
        model = AppTakhali
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","technical_presentation_date")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppTamdeedTable(AppTable):
    menu_name = "profile:app_tamdeed_show"
    relation_fields = []

    class Meta:
        model = AppTamdeed
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","tamdeed_from","tamdeed_to")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppTaaweedTable(AppTable):
    menu_name = "profile:app_taaweed_show"
    relation_fields = []

    class Meta:
        model = AppTaaweed
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","taaweed_from","taaweed_to")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppMdaTable(AppTable):
    menu_name = "profile:app_mda_show"
    relation_fields = []

    class Meta:
        model = AppMda
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","mda_from","mda_to")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppChangeWorkProcedureTable(AppTable):
    menu_name = "profile:app_change_work_procedure_show"
    relation_fields = []

    class Meta:
        model = AppChangeWorkProcedure
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","reason_for_change","purpose_for_change","rational_reason")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

    def render_reason_for_change(self,value):
        return value[:30]

    def render_purpose_for_change(self,value):
        return value[:30]

    def render_rational_reason(self,value):
        return value[:30]

class AppExportGoldTable(AppTable):
    menu_name = "profile:app_export_gold_show"
    relation_fields = []

    class Meta:
        model = AppExportGold
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","total_in_gram","net_in_gram","zakat_in_gram","awaad_jalila_in_gram","arbah_amal_in_gram","sold_for_bank_of_sudan_in_gram","amount_to_export_in_gram","remain_in_gram")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppExportGoldRawTable(AppTable):
    menu_name = "profile:app_export_gold_raw_show"
    relation_fields = []

    class Meta:
        model = AppExportGoldRaw
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","mineral","license_type","amount_in_gram","sale_price","export_country","export_city")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppSendSamplesForAnalysisTable(AppTable):
    menu_name = "profile:app_send_samples_for_analysis_show"
    relation_fields = []

    class Meta:
        model = AppSendSamplesForAnalysis
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","lab_country","lab_city","lab_analysis_cost")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppForeignerProcedureTable(AppTable):
    menu_name = "profile:app_foreigner_procedure_show"
    relation_fields = ['procedure_type']

    class Meta:
        model = AppForeignerProcedure
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","procedure_type","procedure_from","procedure_to")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppAifaaJomrkiTable(AppTable):
    menu_name = "profile:app_aifaa_jomrki_show"
    relation_fields = []

    class Meta:
        model = AppAifaaJomrki
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","license_type")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppReexportEquipmentsTable(AppTable):
    menu_name = "profile:app_reexport_equipments_show"
    relation_fields = []

    class Meta:
        model = AppReexportEquipments
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","cause_for_equipments")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

    def render_cause_for_equipments(self,value):
        return value[:30]

class AppRequirementsListTable(AppTable):
    menu_name = "profile:app_requirements_list_show"
    relation_fields = []

    class Meta:
        model = AppRequirementsList
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppVisibityStudyTable(AppTable):
    menu_name = "profile:app_visibility_study_show"
    relation_fields = ["license_type"]

    class Meta:
        model = AppVisibityStudy
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","license_type","study_area","study_type")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppTemporaryExemptionTable(AppTable):
    menu_name = "profile:app_temporary_exemption_show"
    relation_fields = []

    class Meta:
        model = AppTemporaryExemption
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppLocalPurchaseTable(AppTable):
    menu_name = "profile:app_local_purchase_show"
    relation_fields = []

    class Meta:
        model = AppLocalPurchase
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppCyanideCertificateTable(AppTable):
    menu_name = "profile:app_cyanide_certificate_show"
    relation_fields = []

    class Meta:
        model = AppCyanideCertificate
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppExplosivePermissionTable(AppTable):
    menu_name = "profile:app_explosive_permission_show"
    relation_fields = []

    class Meta:
        model = AppExplosivePermission
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppRestartActivityTable(AppTable):
    menu_name = "profile:app_restart_activity_show"
    relation_fields = []

    class Meta:
        model = AppRestartActivity
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppRenewalContractTable(AppTable):
    menu_name = "profile:app_renewal_contract_show"
    relation_fields = []

    class Meta:
        model = AppRenewalContract
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppImportPermissionTable(AppTable):
    menu_name = "profile:app_import_permission_show"
    relation_fields = []

    class Meta:
        model = AppImportPermission
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppFuelPermissionTable(AppTable):
    menu_name = "profile:app_fuel_permission_show"
    relation_fields = []

    class Meta:
        model = AppFuelPermission
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppHSEAccidentReportTable(AppTable):
    menu_name = "profile:app_hse_accident_show"
    relation_fields = []

    class Meta:
        model = AppHSEAccidentReport
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","accident_dt","accident_place","accident_type","accident_class")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppHSEPerformanceReportTable(AppTable):
    menu_name = "profile:app_hse_performance_show"
    relation_fields = []

    class Meta:
        model = AppHSEPerformanceReport
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","created_at")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppWhomConcernTable(AppTable):
    menu_name = "profile:app_whom_concern_show"
    relation_fields = []

    class Meta:
        model = AppWhomConcern
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","whom_reason")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppGoldProductionTable(AppTable):
    menu_name = "profile:app_gold_production_show"
    relation_fields = []

    class Meta:
        model = AppGoldProduction
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","form_no")
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)
