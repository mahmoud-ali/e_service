from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompanyProduction

from ..models import TblCompanyRequest

class TblCompanyRequestAdminForm(ModelForm):
    class Meta:
        model = TblCompanyRequest
        fields = ["commitement","from_dt","to_dt","amount","currency"] 
        
class TblCompanyRequestForm(TblCompanyRequestAdminForm):
    class Meta:
        model = TblCompanyRequest        
        fields = ["commitement","from_dt","to_dt","amount","currency"] 
        widgets = {
            "from_dt":AdminDateWidget(),
            "to_dt":AdminDateWidget(),
        }
