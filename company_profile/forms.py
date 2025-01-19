from django import forms
from django.forms import ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _

from bootstrap_datepicker_plus.widgets import DatePickerInput

from django_fsm import can_proceed

from .workflow import SUBMITTED,ACCEPTED,APPROVED,REJECTED,WorkflowFormMixin

from .models import AppFuelPermission, AppGoldProduction, AppHSEAccidentReport, AppHSEPerformanceReport, AppImportPermission, AppRenewalContract, AppRestartActivity, AppWhomConcern, TblCompanyProduction, AppForignerMovement,AppBorrowMaterial,AppWorkPlan,AppTechnicalFinancialReport,AppChangeCompanyName, \
                    AppExplorationTime, AppAddArea, AppRemoveArea, AppTnazolShraka, AppTajeelTnazol,AppTajmeed,AppTakhali,AppTamdeed, \
                    AppTaaweed,AppMda,AppChangeWorkProcedure,AppExportGold,AppExportGoldRaw,AppSendSamplesForAnalysis,AppForeignerProcedure, \
                    AppAifaaJomrki,AppReexportEquipments,AppRequirementsList,TblCompanyProductionLicense,AppVisibityStudy, \
                    AppTemporaryExemption,AppLocalPurchase,AppCyanideCertificate,AppExplosivePermission

class LanguageForm(forms.Form):
    LANG_AR = "ar"
    LANG_EN = "en"

    LANG_CHOICES = {
        LANG_AR: _("Arabic"),
        LANG_AR: _("English"),
    }

    language = forms.CharField(max_length=2)

class TblCompanyProductionForm(ModelForm):
    company_type = forms.ChoiceField(choices=[],label=_("company_type"))
    def __init__(self, *args,company_id = None, **kwargs):        
        super().__init__(*args, **kwargs)
        if self.choices:
            self.fields["company_type"].choices = self.choices

    class Meta:
        model = TblCompanyProduction
        fields = "__all__"
             
    def clean(self):
        cleaned_data = super().clean()
        state = cleaned_data.get("state","reject_comments")        
        locality = cleaned_data.get("locality") 
        
        # if state.id != locality.state.id:
        #     self.add_error('locality', _('locality not belong to right state.')+' ('+state.name+')')
           
class AppForignerMovementAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppForignerMovement
        fields = ["company","route_from","route_to","period_from","period_to","address_in_sudan","nationality","passport_no","passport_expiry_date","state","reject_comments","official_letter_file","passport_copy_file","cv_file","experiance_certificates_file"] 
        
class AppForignerMovementForm(AppForignerMovementAdminForm):
    company = None
    class Meta:
        model = AppForignerMovement        
        exclude = ["company","state","reject_comments"]
        widgets = {
            "period_from":DatePickerInput(),
            "period_to":DatePickerInput(),
            "passport_expiry_date":DatePickerInput(),
        }
        
class AppBorrowMaterialAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    company_from = forms.ModelChoiceField(queryset=None, label=_("company_borrow_from"), required=False)
    def __init__(self, *args,company_id = None, **kwargs):        
        super().__init__(*args, **kwargs)
        #company_id = None
        if kwargs.get('company_id'):
            company_id = kwargs.get('company_id')
        elif kwargs.get('instance') and kwargs['instance'].pk:
            company_id = kwargs['instance'].company.id
        
        if company_id:
            self.fields["company_from"].queryset = TblCompanyProduction.objects.exclude(id=company_id)

    class Meta:
        model = AppBorrowMaterial
        fields = ["company","company_from","company_from_str","borrow_date","state","reject_comments","reject_comments","borrow_materials_list_file","borrow_from_approval_file"]
        

class AppBorrowMaterialForm(AppBorrowMaterialAdminForm):
    layout = ["company_from_str","borrow_date",["borrow_materials_list_file","borrow_from_approval_file"]]
    company = None
    class Meta:
        model = AppBorrowMaterial        
        exclude = ["company","state","reject_comments","company_from"]
        widgets = {
            "borrow_date":DatePickerInput(),
        }
        
class AppWorkPlanAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppWorkPlan
        fields = ["company","plan_from","plan_to","plan_comments","state","reject_comments","official_letter_file","work_plan_file"] 
        
class AppWorkPlanForm(AppWorkPlanAdminForm):
    layout = [["plan_from","plan_to"],"plan_comments",["official_letter_file","work_plan_file"]]
    company = None
    class Meta:
        model = AppWorkPlan        
        exclude = ["company","state","reject_comments"]
        widgets = {
            "plan_from":DatePickerInput(),
            "plan_to":DatePickerInput(),
        }

class AppTechnicalFinancialReportAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppTechnicalFinancialReport
        fields = ["company","report_type","report_from","report_to","report_comments","state","reject_comments","report_file","other_attachments_file"] 
        
class AppTechnicalFinancialReportForm(AppTechnicalFinancialReportAdminForm):
    layout = ["report_type",["report_from","report_to"],"report_comments",["report_file","other_attachments_file"]]
    company = None
    class Meta:
        model = AppTechnicalFinancialReport        
        exclude = ["company","state","reject_comments"]
        widgets = {
            "report_from":DatePickerInput(),
            "report_to":DatePickerInput(),
        }

class AppChangeCompanyNameAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppChangeCompanyName
        fields = ["company","new_name","cause_for_change","state","reject_comments","tasis_certificate_file","tasis_contract_file","sh7_file","lahat_tasis_file","name_change_alert_file"] 
        
class AppChangeCompanyNameForm(AppChangeCompanyNameAdminForm):
    layout = ["new_name","cause_for_change",["tasis_certificate_file","tasis_contract_file","sh7_file"],["lahat_tasis_file","name_change_alert_file",""]]
    company = None
    class Meta:
        model = AppChangeCompanyName        
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppExplorationTimeAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppExplorationTime
        fields = ["company","expo_from","expo_to","expo_cause_for_timing","state","reject_comments","expo_cause_for_change_file"] 
        
class AppExplorationTimeForm(AppExplorationTimeAdminForm):
    layout = [["expo_from","expo_to"],"expo_cause_for_timing","expo_cause_for_change_file"] 
    company = None
    class Meta:
        model = AppExplorationTime        
        exclude = ["company","state","reject_comments"]
        widgets = {
            "expo_from":DatePickerInput(),
            "expo_to":DatePickerInput(),
        }

class AppAddAreaAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppAddArea
        fields = ["company","area_in_km2","cause_for_addition","state","reject_comments","geo_coordination_file"] 
        
class AppAddAreaForm(AppAddAreaAdminForm):
    company = None
    class Meta:
        model = AppAddArea        
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppRemoveAreaAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppRemoveArea
        fields = ["company","remove_type","area_in_km2","area_percent_from_total","state","reject_comments","geo_coordinator_for_removed_area_file", "geo_coordinator_for_remain_area_file","map_for_clarification_file","technical_report_for_removed_area_file"] 
        
class AppRemoveAreaForm(AppRemoveAreaAdminForm):
    layout = ["remove_type","area_in_km2","area_percent_from_total",["geo_coordinator_for_removed_area_file", "geo_coordinator_for_remain_area_file"],["map_for_clarification_file","technical_report_for_removed_area_file"]]
    company = None
    class Meta:
        model = AppRemoveArea        
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppTnazolShrakaAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppTnazolShraka
        fields = ["company","tnazol_type","tnazol_for","cause_for_tnazol","state","reject_comments","financial_ability_file", "cv_file","agreement_file"] 
        
class AppTnazolShrakaForm(AppTnazolShrakaAdminForm):
    company = None
    class Meta:
        model = AppTnazolShraka        
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppTajeelTnazolAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppTajeelTnazol
        fields = ["company","tnazol_type","cause_for_tajeel","state","reject_comments","cause_for_tajeel_file"]
        
class AppTajeelTnazolForm(AppTajeelTnazolAdminForm):
    company = None
    class Meta:
        model = AppTajeelTnazol        
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppTajmeedAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppTajmeed
        fields = ["company","tajmeed_from","tajmeed_to","cause_for_tajmeed","state","reject_comments","cause_for_uncontrolled_force_file","letter_from_jeha_amnia_file"] 
        
class AppTajmeedForm(AppTajmeedAdminForm):
    layout = [["tajmeed_from","tajmeed_to"],"cause_for_tajmeed",["cause_for_uncontrolled_force_file","letter_from_jeha_amnia_file"]]
    company = None
    class Meta:
        model = AppTajmeed        
        exclude = ["company","state","reject_comments"]
        widgets = {
            "tajmeed_from":DatePickerInput(),
            "tajmeed_to":DatePickerInput(),
        }

class AppTakhaliAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppTakhali
        fields = ["company","technical_presentation_date","cause_for_takhali","state","reject_comments","technical_report_file"]
        
class AppTakhaliForm(AppTakhaliAdminForm):
    company = None
    class Meta:
        model = AppTakhali        
        exclude = ["company","state","reject_comments"]
        widgets = {
            "technical_presentation_date":DatePickerInput(),
        }

class AppTamdeedAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppTamdeed
        fields = ["company","tamdeed_from","tamdeed_to","cause_for_tamdeed","state","reject_comments","approved_work_plan_file","tnazol_file"] 
        
class AppTamdeedForm(AppTamdeedAdminForm):
    layout = [["tamdeed_from","tamdeed_to"],"cause_for_tamdeed",["approved_work_plan_file","tnazol_file"]]
    company = None
    class Meta:
        model = AppTamdeed        
        exclude = ["company","state","reject_comments"]
        widgets = {
            "tamdeed_from":DatePickerInput(),
            "tamdeed_to":DatePickerInput(),
        }

class AppTaaweedAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppTaaweed
        fields = ["company","taaweed_from","taaweed_to","cause_for_taaweed","state","reject_comments"] 
        
class AppTaaweedForm(AppTaaweedAdminForm):
    layout = [["taaweed_from","taaweed_to"],"cause_for_taaweed"] 
    company = None
    class Meta:
        model = AppTaaweed        
        exclude = ["company","state","reject_comments"]
        widgets = {
            "taaweed_from":DatePickerInput(),
            "taaweed_to":DatePickerInput(),
        }

class AppMdaAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppMda
        fields = ["company","mda_from","mda_to","cause_for_mda","state","reject_comments","approved_work_plan_file"] 
        
class AppMdaForm(AppMdaAdminForm):
    layout = [["mda_from","mda_to"],"cause_for_mda","approved_work_plan_file"] 
    company = None
    class Meta:
        model = AppMda
        exclude = ["company","state","reject_comments"]
        widgets = {
            "mda_from":DatePickerInput(),
            "mda_to":DatePickerInput(),
        }

class AppChangeWorkProcedureAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppChangeWorkProcedure
        fields = ["company","reason_for_change","purpose_for_change","rational_reason","state","reject_comments","study_about_change_reason_file","study_about_new_suggestion_file"] 
        
class AppChangeWorkProcedureForm(AppChangeWorkProcedureAdminForm):
    company = None
    class Meta:
        model = AppChangeWorkProcedure
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppExportGoldAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppExportGold
        fields = ["company","total_in_gram","net_in_gram","zakat_in_gram", "awaad_jalila_in_gram","sold_for_bank_of_sudan_in_gram", "amount_to_export_in_gram","remain_in_gram","arbah_amal_in_gram","state","reject_comments", "f1","f3","f4","f6","f7","f8","f9","f5"] 
        
class AppExportGoldForm(AppExportGoldAdminForm):
    company = None
    class Meta:
        model = AppExportGold
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppExportGoldRawAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppExportGoldRaw
        fields = ["company","mineral","license_type","amount_in_gram","sale_price","export_country","export_city","export_address","state","reject_comments", "f11","f12","f13","f14","f15","f16","f17","f18","f19"] 
        
class AppExportGoldRawForm(AppExportGoldRawAdminForm):
    company = None
    class Meta:
        model = AppExportGoldRaw
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppSendSamplesForAnalysisAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppSendSamplesForAnalysis
        fields = ["company","lab_country","lab_city","lab_address","lab_analysis_cost","state","reject_comments","initial_voucher_file","sample_description_form_file","last_analysis_report_file"] 
        
class AppSendSamplesForAnalysisForm(AppSendSamplesForAnalysisAdminForm):
    company = None
    class Meta:
        model = AppSendSamplesForAnalysis
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppForeignerProcedureAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppForeignerProcedure
        fields = ["company","procedure_type","procedure_from","procedure_to","procedure_cause","state","reject_comments", "official_letter_file","passport_file","cv_file","experience_certificates_file","eqama_file","dawa_file"] 
        
class AppForeignerProcedureForm(AppForeignerProcedureAdminForm):
    layout = ["procedure_type",["procedure_from","procedure_to"],"procedure_cause",["official_letter_file","passport_file","cv_file"],["experience_certificates_file","eqama_file","dawa_file"]]
    company = None
    class Meta:
        model = AppForeignerProcedure
        exclude = ["company","state","reject_comments"]
        widgets = {
            "procedure_from":DatePickerInput(),
            "procedure_to":DatePickerInput(),
        }

class AppAifaaJomrkiAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    license_type = forms.ModelChoiceField(queryset=None, label=_("license_type"))
    def __init__(self, *args,company_id = None, **kwargs):        
        super().__init__(*args, **kwargs)

        if kwargs.get('company_id'):
            company_id = kwargs.get('company_id')
        elif kwargs.get('instance') and kwargs['instance'].pk:
            company_id = kwargs['instance'].company.id
        
        if company_id:
            self.fields["license_type"].queryset = TblCompanyProductionLicense.objects.filter(company__id=company_id)

    class Meta:
        model = AppAifaaJomrki
        fields = ["company","license_type","state","reject_comments", "approved_requirements_list_file", "approval_from_finance_ministry_file","final_voucher_file", "shipping_policy_file","check_certificate_file","origin_certificate_file", "packing_certificate_file","specifications_file","taba_file"] 
        
class AppAifaaJomrkiForm(AppAifaaJomrkiAdminForm):
    layout = ["license_type", ["approved_requirements_list_file", "approval_from_finance_ministry_file","final_voucher_file", "shipping_policy_file"],["check_certificate_file","origin_certificate_file", "packing_certificate_file","specifications_file"],"taba_file"] 
    company = None
    class Meta:
        model = AppAifaaJomrki
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppReexportEquipmentsAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppReexportEquipments
        fields = ["company","cause_for_equipments","state","reject_comments", "shipping_policy_file", "voucher_file","specifications_file"] 
        
class AppReexportEquipmentsForm(AppReexportEquipmentsAdminForm):
    layout = ["cause_for_equipments", ["shipping_policy_file", "voucher_file","specifications_file"]] 
    company = None
    class Meta:
        model = AppReexportEquipments
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppRequirementsListAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    class Meta:
        model = AppRequirementsList
        fields = ["company","state","reject_comments", "approved_work_plan_file", "initial_voucher_file","specifications_file", "mshobat_jamarik_file"] 
        
class AppRequirementsListForm(AppRequirementsListAdminForm):
    layout = [["approved_work_plan_file", "initial_voucher_file"],["specifications_file", "mshobat_jamarik_file"]]
    company = None
    class Meta:
        model = AppRequirementsList
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppVisibityStudyAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))
    license_type = forms.ModelChoiceField(queryset=None, label=_("license_type"))
    def __init__(self, *args,company_id = None, **kwargs):        
        super().__init__(*args, **kwargs)

        if kwargs.get('company_id'):
            company_id = kwargs.get('company_id')
        elif kwargs.get('instance') and kwargs['instance'].pk:
            company_id = kwargs['instance'].company.id
        
        if company_id:
            self.fields["license_type"].queryset = TblCompanyProductionLicense.objects.filter(company__id=company_id)

    class Meta:
        model = AppVisibityStudy
        fields = ["company","license_type","study_area", "study_type", "study_comment","state","reject_comments","attachement_file"] 
        
class AppVisibityStudyForm(AppVisibityStudyAdminForm):
    company = None
    class Meta:
        model = AppVisibityStudy
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppTemporaryExemptionAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppTemporaryExemption
        fields = ["company","state","reject_comments","attachement_file"] 
        
class AppTemporaryExemptionForm(AppTemporaryExemptionAdminForm):
    company = None
    class Meta:
        model = AppTemporaryExemption
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppLocalPurchaseAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppLocalPurchase
        fields = ["company","state","reject_comments","attachement_file","attachement_file2"] 
        
class AppLocalPurchaseForm(AppLocalPurchaseAdminForm):
    company = None
    class Meta:
        model = AppLocalPurchase
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppCyanideCertificateAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppCyanideCertificate
        fields = ["company","state","reject_comments","attachement_file"] 
        
class AppCyanideCertificateForm(AppCyanideCertificateAdminForm):
    company = None
    class Meta:
        model = AppCyanideCertificate
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppExplosivePermissionAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppExplosivePermission
        fields = ["company","state","reject_comments","attachement_file","attachement_file2","attachement_file3"] 
        
class AppExplosivePermissionForm(AppExplosivePermissionAdminForm):
    company = None
    class Meta:
        model = AppExplosivePermission
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppRestartActivityAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppRestartActivity
        fields = ["company","state","reject_comments","attachement_file"] 
        
class AppRestartActivityForm(AppRestartActivityAdminForm):
    company = None
    class Meta:
        model = AppRestartActivity
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppRenewalContractAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppRenewalContract
        fields = ["company","state","reject_comments","attachement_file"] 
        
class AppRenewalContractForm(AppRenewalContractAdminForm):
    company = None
    class Meta:
        model = AppRenewalContract
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppImportPermissionAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppImportPermission
        fields = ["company","state","reject_comments","attachement_file"] 
        
class AppImportPermissionForm(AppImportPermissionAdminForm):
    company = None
    class Meta:
        model = AppImportPermission
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppFuelPermissionAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppFuelPermission
        fields = ["company","state","reject_comments","attachement_file"] 
        
class AppFuelPermissionForm(AppFuelPermissionAdminForm):
    company = None
    class Meta:
        model = AppFuelPermission
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppHSEAccidentReportAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppHSEAccidentReport
        fields = ["company","accident_dt","accident_place","accident_type","accident_class","reject_comments","state","attachement_file"] 
        
class AppHSEAccidentReportForm(AppHSEAccidentReportAdminForm):
    company = None
    class Meta:
        model = AppHSEAccidentReport
        exclude = ["company","state","reject_comments"]
        widgets = {
            "accident_dt":DatePickerInput(),
        }

class AppHSEPerformanceReportAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppHSEPerformanceReport
        fields = ["company","state","reject_comments"] #,"attachement_file"
        
class AppHSEPerformanceReportForm(AppHSEPerformanceReportAdminForm):
    company = None
    class Meta:
        model = AppHSEPerformanceReport
        exclude = ["company","state","reject_comments"]
        widgets = {}

class AppWhomConcernAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppWhomConcern
        fields = ["company","whom_reason","whom_subject","whom_attachement_file","state","reject_comments"] 
        
class AppWhomConcernForm(AppWhomConcernAdminForm):
    company = None
    class Meta:
        model = AppWhomConcern
        exclude = ["company","state","reject_comments"] #,"whom_attachement_file"
        widgets = {}

class AppGoldProductionAdminForm(WorkflowFormMixin,ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), disabled=True, label=_("company"))

    class Meta:
        model = AppGoldProduction
        fields = ["company","form_no","attachement_file","state","reject_comments"] 
        
class AppGoldProductionForm(AppGoldProductionAdminForm):
    company = None
    class Meta:
        model = AppGoldProduction
        exclude = ["company","state","reject_comments"]
        widgets = {}
