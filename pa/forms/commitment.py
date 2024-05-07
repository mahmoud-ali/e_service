from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from bootstrap_datepicker_plus.widgets import DatePickerInput

from company_profile.models import TblCompanyProduction, TblCompanyProductionLicense

from ..models import STATE_TYPE_CONFIRM, TblCompanyCommitmentDetail, TblCompanyCommitmentMaster, TblCompanyCommitmentSchedular

commitment_all_qs = TblCompanyCommitmentMaster.objects.prefetch_related("company")
commitment_confirmed_qs = commitment_all_qs.filter(state=STATE_TYPE_CONFIRM)

class TblCompanyCommitmentAdminForm(ModelForm):
    # company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), label=_("company"))
    class Meta:
        model = TblCompanyCommitmentMaster
        fields = ["company","license","currency","state"] 
        
class TblCompanyAddCommitmentForm(TblCompanyCommitmentAdminForm):
    # company = None
    layout = [["company","license","currency"]]
    class Meta:
        model = TblCompanyCommitmentMaster     
        fields = ["company","license","currency"] 
        widgets = {}

    def __init__(self, *args,company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company_id:
            self.fields["company"].queryset = TblCompanyProduction.objects.filter(id=company_id)
            self.fields["license"].queryset = TblCompanyProductionLicense.objects.filter(company__id=company_id)
        else:
            self.fields["company"].queryset = TblCompanyProduction.objects.none()
            self.fields["license"].queryset = TblCompanyProductionLicense.objects.none()

class TblCompanyShowEditCommitmentForm(TblCompanyCommitmentAdminForm):
    # company = None
    layout = [["company","license","currency"]]
    class Meta:
        model = TblCompanyCommitmentMaster     
        fields = ["company","license","currency"] 
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('instance') and kwargs['instance'].pk:
            pk = kwargs['instance'].company.id
        
        if pk:
            self.fields["company"].queryset = TblCompanyProduction.objects.filter(id=pk)
            self.fields["license"].queryset = TblCompanyProductionLicense.objects.filter(company__id=pk)
        else:
            self.fields["company"].queryset = TblCompanyProduction.objects.none()
            self.fields["license"].queryset = TblCompanyProductionLicense.objects.none()

class TblCompanyCommitmentDetailForm(ModelForm):
    class Meta:
        model = TblCompanyCommitmentDetail     
        fields = ["item","amount_factor"] 
        widgets = {}

class TblCompanyRequestChooseCompanyForm(forms.Form):
    layout = [["company",""]]
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all().order_by("name_ar"), label=_("company"))
    class Meta:
        model = TblCompanyCommitmentMaster      
        fields = ["company"] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].widget.attrs.update({"class": "select2"})

class TblCompanyCommitmentScheduleForm(ModelForm):
    commitment = forms.ModelChoiceField(queryset=commitment_confirmed_qs.order_by("company"), label=_("commitment")) 
    class Meta:
        model = TblCompanyCommitmentSchedular     
        fields = ["commitment","request_interval","request_next_interval_dt","request_auto_confirm"] 
        widgets = {
            "request_next_interval_dt":DatePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commitment"].widget.attrs.update({"class": "select2"})
