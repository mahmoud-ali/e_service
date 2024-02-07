from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from django_fsm import can_proceed

from .workflow import SUBMITTED,ACCEPTED,APPROVED,REJECTED,WorkflowFormMixin

from .models import TblCompanyProduction, AppForignerMovement,AppBorrowMaterial,AppWorkPlan,AppTechnicalFinancialReport,AppChangeCompanyName, \
                    AppExplorationTime, AppAddArea, AppRemoveArea, AppTnazolShraka, AppTajeelTnazol,AppTajmeed,AppTakhali,AppTamdeed, \
                    AppTaaweed,AppMda,AppChangeWorkProcedure,AppExportGold,AppExportGoldRaw,AppSendSamplesForAnalysis,AppForeignerProcedure, \
                    AppAifaaJomrki,AppReexportEquipments

class LanguageForm(forms.Form):
    LANG_AR = "ar"
    LANG_EN = "en"

    LANG_CHOICES = {
        LANG_AR: _("Arabic"),
        LANG_AR: _("English"),
    }

    language = forms.CharField(max_length=2)

class TblCompanyProductionForm(ModelForm):

    class Meta:
        model = TblCompanyProduction
        fields = "__all__"
             
    def clean(self):
        cleaned_data = super().clean()
        state = cleaned_data.get("state")        
        locality = cleaned_data.get("locality") 
        
        if state.id != locality.state.id:
            self.add_error('locality', _('locality not belong to right state.')+' ('+state.name+')')
            
class AppForignerMovementAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppForignerMovement
        fields = ["company","route_from","route_to","period_from","period_to","address_in_sudan","nationality","passport_no","passport_expiry_date","state","official_letter_file","passport_copy_file","cv_file","experiance_certificates_file"] 
        
class AppForignerMovementForm(AppForignerMovementAdminForm):
    class Meta:
        model = AppForignerMovement        
        exclude = ["company","state"]
        widgets = {
            "period_from":AdminDateWidget(),
            "period_to":AdminDateWidget(),
            "passport_expiry_date":AdminDateWidget(),
        }
        
class AppBorrowMaterialAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppBorrowMaterial
        fields = ["company","company_from","borrow_date","state","borrow_materials_list_file","borrow_from_approval_file"]
        

class AppBorrowMaterialForm(AppBorrowMaterialAdminForm):
    class Meta:
        model = AppBorrowMaterial        
        exclude = ["company","state"]
        widgets = {
            "borrow_date":AdminDateWidget(),
        }
        
class AppWorkPlanAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppWorkPlan
        fields = ["company","plan_from","plan_to","state","official_letter_file","work_plan_file"] 
        
class AppWorkPlanForm(AppWorkPlanAdminForm):
    class Meta:
        model = AppWorkPlan        
        exclude = ["company","state"]
        widgets = {
            "plan_from":AdminDateWidget(),
            "plan_to":AdminDateWidget(),
        }

class AppTechnicalFinancialReportAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppTechnicalFinancialReport
        fields = ["company","report_from","report_to","report_type","state","report_file","other_attachments_file"] 
        
class AppTechnicalFinancialReportForm(AppTechnicalFinancialReportAdminForm):
    class Meta:
        model = AppTechnicalFinancialReport        
        exclude = ["company","state"]
        widgets = {
            "report_from":AdminDateWidget(),
            "report_to":AdminDateWidget(),
        }

class AppChangeCompanyNameAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppChangeCompanyName
        fields = ["company","new_name","state","tasis_certificate_file","tasis_contract_file","sh7_file","lahat_tasis_file","name_change_alert_file"] 
        
class AppChangeCompanyNameForm(AppChangeCompanyNameAdminForm):
    class Meta:
        model = AppChangeCompanyName        
        exclude = ["company","state"]
        widgets = {}

class AppExplorationTimeAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppExplorationTime
        fields = ["company","expo_from","expo_to","expo_cause_for_timing","state","expo_cause_for_change_file"] 
        
class AppExplorationTimeForm(AppExplorationTimeAdminForm):
    class Meta:
        model = AppExplorationTime        
        exclude = ["company","state"]
        widgets = {
            "expo_from":AdminDateWidget(),
            "expo_to":AdminDateWidget(),
        }

class AppAddAreaAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppAddArea
        fields = ["company","area_in_km2","cause_for_addition","state","geo_coordination_file"] 
        
class AppAddAreaForm(AppAddAreaAdminForm):
    class Meta:
        model = AppAddArea        
        exclude = ["company","state"]
        widgets = {}

class AppRemoveAreaAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppRemoveArea
        fields = ["company","remove_type","area_in_km2","area_percent_from_total","state","geo_coordinator_for_removed_area_file", "geo_coordinator_for_remain_area_file","map_for_clarification_file","technical_report_for_removed_area_file"] 
        
class AppRemoveAreaForm(AppRemoveAreaAdminForm):
    class Meta:
        model = AppRemoveArea        
        exclude = ["company","state"]
        widgets = {}

class AppTnazolShrakaAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppTnazolShraka
        fields = ["company","tnazol_type","tnazol_for","cause_for_tnazol","state","financial_ability_file", "cv_file"] 
        
class AppTnazolShrakaForm(AppTnazolShrakaAdminForm):
    class Meta:
        model = AppTnazolShraka        
        exclude = ["company","state"]
        widgets = {}

class AppTajeelTnazolAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppTajeelTnazol
        fields = ["company","tnazol_type","cause_for_tajeel","state","cause_for_tajeel_file"]
        
class AppTajeelTnazolForm(AppTajeelTnazolAdminForm):
    class Meta:
        model = AppTajeelTnazol        
        exclude = ["company","state"]
        widgets = {}

class AppTajmeedAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppTajmeed
        fields = ["company","tajmeed_from","tajmeed_to","cause_for_tajmeed","state","cause_for_uncontrolled_force_file","letter_from_jeha_amnia_file"] 
        
class AppTajmeedForm(AppTajmeedAdminForm):
    class Meta:
        model = AppTajmeed        
        exclude = ["company","state"]
        widgets = {
            "tajmeed_from":AdminDateWidget(),
            "tajmeed_to":AdminDateWidget(),
        }

class AppTakhaliAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppTakhali
        fields = ["company","technical_presentation_date","cause_for_takhali","state","technical_report_file"]
        
class AppTakhaliForm(AppTakhaliAdminForm):
    class Meta:
        model = AppTakhali        
        exclude = ["company","state"]
        widgets = {
            "technical_presentation_date":AdminDateWidget(),
        }

class AppTamdeedAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppTamdeed
        fields = ["company","tamdeed_from","tamdeed_to","cause_for_tamdeed","state","approved_work_plan_file","tnazol_file"] 
        
class AppTamdeedForm(AppTamdeedAdminForm):
    class Meta:
        model = AppTamdeed        
        exclude = ["company","state"]
        widgets = {
            "tamdeed_from":AdminDateWidget(),
            "tamdeed_to":AdminDateWidget(),
        }

class AppTaaweedAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppTaaweed
        fields = ["company","taaweed_from","taaweed_to","cause_for_taaweed","state"] 
        
class AppTaaweedForm(AppTaaweedAdminForm):
    class Meta:
        model = AppTaaweed        
        exclude = ["company","state"]
        widgets = {
            "taaweed_from":AdminDateWidget(),
            "taaweed_to":AdminDateWidget(),
        }

class AppMdaAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppMda
        fields = ["company","mda_from","mda_to","cause_for_mda","state","approved_work_plan_file"] 
        
class AppMdaForm(AppMdaAdminForm):
    class Meta:
        model = AppMda
        exclude = ["company","state"]
        widgets = {
            "mda_from":AdminDateWidget(),
            "mda_to":AdminDateWidget(),
        }

class AppChangeWorkProcedureAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppChangeWorkProcedure
        fields = ["company","reason_for_change","purpose_for_change","rational_reason","state","study_about_change_reason_file","study_about_new_suggestion_file"] 
        
class AppChangeWorkProcedureForm(AppChangeWorkProcedureAdminForm):
    class Meta:
        model = AppChangeWorkProcedure
        exclude = ["company","state"]
        widgets = {}

class AppExportGoldAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppExportGold
        fields = ["company","total_in_gram","net_in_gram","zakat_in_gram", "awaad_jalila_in_gram","arbah_amal_in_gram","sold_for_bank_of_sudan_in_gram", "amount_to_export_in_gram","remain_in_gram","state", "f1","f2","f3","f4","f5","f6","f7","f8","f9"] 
        
class AppExportGoldForm(AppExportGoldAdminForm):
    class Meta:
        model = AppExportGold
        exclude = ["company","state"]
        widgets = {}

class AppExportGoldRawAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppExportGoldRaw
        fields = ["company","mineral","license_type","amount_in_gram","sale_price","export_country","export_city","export_address","state", "f11","f12","f13","f14","f15","f16","f17","f18","f19"] 
        
class AppExportGoldRawForm(AppExportGoldRawAdminForm):
    class Meta:
        model = AppExportGoldRaw
        exclude = ["company","state"]
        widgets = {}

class AppSendSamplesForAnalysisAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppSendSamplesForAnalysis
        fields = ["company","lab_country","lab_city","lab_address","lab_analysis_cost","state", "last_analysis_report_file","initial_voucher_file","sample_description_form_file"] 
        
class AppSendSamplesForAnalysisForm(AppSendSamplesForAnalysisAdminForm):
    class Meta:
        model = AppSendSamplesForAnalysis
        exclude = ["company","state"]
        widgets = {}

class AppForeignerProcedureAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppForeignerProcedure
        fields = ["company","procedure_type","procedure_from","procedure_to","procedure_cause","state", "official_letter_file","passport_file","cv_file","experience_certificates_file","eqama_file","dawa_file"] 
        
class AppForeignerProcedureForm(AppForeignerProcedureAdminForm):
    class Meta:
        model = AppForeignerProcedure
        exclude = ["company","state"]
        widgets = {
            "procedure_from":AdminDateWidget(),
            "procedure_to":AdminDateWidget(),
        }

class AppAifaaJomrkiAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppAifaaJomrki
        fields = ["company","license_type","state", "approved_requirements_list_file", "approval_from_finance_ministry_file","final_voucher_file", "shipping_policy_file","check_certificate_file","origin_certificate_file", "packing_certificate_file","specifications_file","taba_file"] 
        
class AppAifaaJomrkiForm(AppAifaaJomrkiAdminForm):
    class Meta:
        model = AppAifaaJomrki
        exclude = ["company","state"]
        widgets = {}

class AppReexportEquipmentsAdminForm(WorkflowFormMixin,ModelForm):
    class Meta:
        model = AppReexportEquipments
        fields = ["company","cause_for_equipments","state", "shipping_policy_file", "voucher_file","specifications_file", "momentary_approval_file"] 
        
class AppReexportEquipmentsForm(AppReexportEquipmentsAdminForm):
    class Meta:
        model = AppReexportEquipments
        exclude = ["company","state"]
        widgets = {}

