from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from ..models import TblCompanyCommitmentMaster, TblCompanyCommitmentSchedular,TblCompanyRequestMaster,STATE_TYPE_CONFIRM

commitment_all_qs = TblCompanyCommitmentMaster.objects.prefetch_related("company")
commitment_confirmed_qs = commitment_all_qs.filter(state=STATE_TYPE_CONFIRM)

class TblCompanyRequestAdminForm(ModelForm):
    class Meta:
        model = TblCompanyRequestMaster
        fields = ["commitment","from_dt","to_dt","currency","state"] 
        
class TblCompanyRequestShowEditForm(TblCompanyRequestAdminForm):
    layout = ["commitment",["from_dt","to_dt"],["currency","total_payment"]]
    commitment = forms.ModelChoiceField(queryset=None,disabled=True, label=_("commitment"))
    total_payment = forms.FloatField(label=_('payments total'),disabled=True)
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)
        pk = None

        if kwargs.get('instance') and kwargs['instance'].pk:
            pk = kwargs['instance'].commitment.id
        
        if pk:
            self.fields["commitment"].queryset = commitment_all_qs.filter(id=pk)
            self.fields["total_payment"].initial = kwargs['instance'].sum_of_payment()
        else:
            self.fields["total_payment"].initial = 0.0

    class Meta:
        model = TblCompanyRequestMaster
        fields = ["commitment","from_dt","to_dt","currency"] 
        widgets = {
            "from_dt":AdminDateWidget(),
            "to_dt":AdminDateWidget(),
        }

class TblCompanyRequestAddForm(TblCompanyRequestAdminForm):
    layout = ["commitment",["from_dt","to_dt"],["currency"]]
    commitment = forms.ModelChoiceField(queryset=commitment_confirmed_qs.order_by("company"), label=_("commitment")) #.filter(commitment_schedular__request_interval=TblCompanyCommitmentSchedular.INTERVAL_TYPE_MANUAL)
    class Meta:
        model = TblCompanyRequestMaster      
        fields = ["commitment","from_dt","to_dt","currency"] 
        widgets = {
            "from_dt":AdminDateWidget(),
            "to_dt":AdminDateWidget(),
        }

class TblCompanyRequestChooseCommitmentForm(forms.Form):
    layout = ["commitment"]
    commitment = forms.ModelChoiceField(queryset=commitment_confirmed_qs.order_by("company"), label=_("commitment")) #.filter(commitment_schedular__request_interval=TblCompanyCommitmentSchedular.INTERVAL_TYPE_MANUAL)
    class Meta:
        model = TblCompanyRequestMaster      
        fields = ["commitment"] 

