from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from bootstrap_datepicker_plus.widgets import DatePickerInput

from company_profile.models import TblCompany, TblCompanyProduction, TblCompanyProductionLicense

from ..models import ApplicationExectiveProcessing,Department,ActionType

class ApplicationExectiveProcessingAdminForm(ModelForm):
    class Meta:
        model = ApplicationExectiveProcessing
        fields = ["department","action_type","attachement_file"]
        
class ApplicationExectiveProcessingAddForm(ApplicationExectiveProcessingAdminForm):
    layout = [["department","action_type"],"attachement_file"]
    class Meta:
        model = ApplicationExectiveProcessing     
        fields = ["department","action_type","attachement_file"] 
        widgets = {}

class ApplicationExectiveProcessingShowEditForm(ApplicationExectiveProcessingAdminForm):
    layout = [["department","action_type"],["main_attachement_file","attachement_file"]]
    department = forms.ModelChoiceField(queryset=Department.objects.all(), disabled=True, label=_("department"))
    action_type = forms.ModelChoiceField(queryset=ActionType.objects.all(), disabled=True, label=_("action_type"))
    main_attachement_file = forms.FileField(label=_("main_attachement_file"), disabled=True)
    class Meta:
        model = ApplicationExectiveProcessing     
        fields = ["department","action_type","main_attachement_file","attachement_file"]
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['main_attachement_file'].initial = instance.department_processing.app_record.attachement_file
