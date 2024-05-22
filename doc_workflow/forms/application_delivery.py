from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from bootstrap_datepicker_plus.widgets import DatePickerInput

from company_profile.models import TblCompany, TblCompanyProduction, TblCompanyProductionLicense

from ..models import ApplicationDelivery,Department,ActionType

class ApplicationDeliveryAdminForm(ModelForm):
    class Meta:
        model = ApplicationDelivery
        fields = ["app_record","destination"]
        
class ApplicationDeliveryAddForm(ApplicationDeliveryAdminForm):
    layout = [["app_record","department","action_type"],"attachement_file"]
    class Meta:
        model = ApplicationDelivery     
        fields = ["app_record","destination"] 
        widgets = {}

class ApplicationDeliveryShowEditForm(ApplicationDeliveryAdminForm):
    layout = [["app_record","destination"]]
    class Meta:
        model = ApplicationDelivery     
        fields = ["app_record","destination"]
        widgets = {}

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     instance = getattr(self, 'instance', None)
    #     if instance and instance.pk:
    #         self.fields['department'].widget.attrs['disabled'] = True
    #         self.fields['action_type'].widget.attrs['disabled'] = True