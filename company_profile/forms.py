from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from django_fsm import can_proceed

from .workflow import SUBMITTED,ACCEPTED,APPROVED,REJECTED,WorkflowFormMixin

from .models import TblCompanyProduction, AppForignerMovement,AppBorrowMaterial

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
        
