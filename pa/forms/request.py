from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from bootstrap_datepicker_plus.widgets import DatePickerInput

from ..models import LkpItem, TblCompanyCommitmentMaster, TblCompanyCommitmentSchedular, TblCompanyRequestDetail,TblCompanyRequestMaster,STATE_TYPE_CONFIRM,STATE_TYPE_DRAFT

commitment_none = TblCompanyCommitmentMaster.objects.none()
commitment_all_qs = TblCompanyCommitmentMaster.objects.prefetch_related("company")
commitment_confirmed_qs = commitment_all_qs.filter(state=STATE_TYPE_CONFIRM)
commitment_confirmed_manual_qs = commitment_confirmed_qs \
    .filter(
        Q(commitment_schedular__isnull=True)|
        Q(commitment_schedular__state=STATE_TYPE_DRAFT)|
        Q(
            commitment_schedular__request_interval=TblCompanyCommitmentSchedular.INTERVAL_TYPE_MANUAL, \
            commitment_schedular__state=STATE_TYPE_CONFIRM
        )
    )
item_none = LkpItem.objects.none()
item_all_qs = LkpItem.objects.all()

class TblCompanyRequestAdminForm(ModelForm):
    class Meta:
        model = TblCompanyRequestMaster
        fields = ["commitment","from_dt","to_dt","currency","note","attachement_file"] #,"state"
        
class TblCompanyRequestShowEditForm(TblCompanyRequestAdminForm):
    layout = ["commitment",["from_dt","to_dt"],["currency","total_payment"],"note","attachement_file"]
    commitment = forms.ModelChoiceField(queryset=commitment_none,disabled=True, label=_("commitment"))
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
        fields = ["commitment","from_dt","to_dt","currency","note","attachement_file"] 
        widgets = {
            "from_dt":DatePickerInput(),
            "to_dt":DatePickerInput(),
        }

class TblCompanyRequestAddForm(TblCompanyRequestAdminForm):
    layout = ["commitment",["from_dt","to_dt"],["currency"],"note","attachement_file"]
    commitment = forms.ModelChoiceField(queryset=commitment_none, label=_("commitment")) #.filter(commitment_schedular__request_interval=TblCompanyCommitmentSchedular.INTERVAL_TYPE_MANUAL)
    class Meta:
        model = TblCompanyRequestMaster      
        fields = ["commitment","from_dt","to_dt","currency","note","attachement_file"] 
        widgets = {
            "from_dt":DatePickerInput(),
            "to_dt":DatePickerInput(),
        }

    def __init__(self, *args,commitment_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if commitment_id:
            self.fields["commitment"].queryset = commitment_all_qs.filter(id=commitment_id)

class TblCompanyRequestDetailsForm(ModelForm):
    item = forms.ModelChoiceField(queryset=item_none,disabled=True, label=_("item"))
    company_type = None
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

        self.fields["item"].queryset = item_all_qs.filter(company_type=self.company_type)
        self.fields["item"].disabled = False

    class Meta:
        model = TblCompanyRequestDetail
        fields = ['item','amount'] 

class TblCompanyRequestChooseCommitmentForm(forms.Form):
    layout = [["commitment",""]]
    commitment = forms.ModelChoiceField(queryset=commitment_confirmed_manual_qs.order_by("company"), label=_("commitment")) #.filter(commitment_schedular__request_interval=TblCompanyCommitmentSchedular.INTERVAL_TYPE_MANUAL)
    class Meta:
        model = TblCompanyRequestMaster      
        fields = ["commitment"] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commitment"].widget.attrs.update({"class": "select2"})
