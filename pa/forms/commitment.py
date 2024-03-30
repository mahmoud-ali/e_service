from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompanyProduction

from ..models import TblCompanyCommitment

class TblCompanyCommitmentAdminForm(ModelForm):
    # company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), label=_("company"))
    class Meta:
        model = TblCompanyCommitment
        fields = ["company","item","amount","currency","request_interval","request_next_interval_dt","request_auto_confirm"] 
        
class TblCompanyCommitmentForm(TblCompanyCommitmentAdminForm):
    # company = None
    class Meta:
        model = TblCompanyCommitment        
        fields = ["company","item","amount","currency","request_interval","request_next_interval_dt","request_auto_confirm"] 
        widgets = {
            "request_next_interval_dt":AdminDateWidget(),
        }
