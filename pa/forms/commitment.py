from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompanyProduction

from ..models import STATE_TYPE_CONFIRM, TblCompanyCommitmentDetail, TblCompanyCommitmentMaster, TblCompanyCommitmentSchedular

commitment_all_qs = TblCompanyCommitmentMaster.objects.prefetch_related("company")
commitment_confirmed_qs = commitment_all_qs.filter(state=STATE_TYPE_CONFIRM)

class TblCompanyCommitmentAdminForm(ModelForm):
    # company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), label=_("company"))
    class Meta:
        model = TblCompanyCommitmentMaster
        fields = ["company","currency","state"] 
        
class TblCompanyCommitmentForm(TblCompanyCommitmentAdminForm):
    # company = None
    layout = [["company","currency"]]
    class Meta:
        model = TblCompanyCommitmentMaster     
        fields = ["company","currency"] 
        widgets = {}

class TblCompanyCommitmentDetailForm(ModelForm):
    class Meta:
        model = TblCompanyCommitmentDetail     
        fields = ["item","amount_factor"] 
        widgets = {}

class TblCompanyCommitmentScheduleForm(ModelForm):
    commitment = forms.ModelChoiceField(queryset=commitment_confirmed_qs.order_by("company"), label=_("commitment")) 
    class Meta:
        model = TblCompanyCommitmentSchedular     
        fields = ["commitment","request_interval","request_next_interval_dt","request_auto_confirm"] 
        widgets = {
            "request_next_interval_dt":AdminDateWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commitment"].widget.attrs.update({"class": "select2"})
