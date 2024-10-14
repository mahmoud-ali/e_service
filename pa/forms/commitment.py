from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from bootstrap_datepicker_plus.widgets import DatePickerInput

from company_profile.models import TblCompanyProduction, TblCompanyProductionLicense
from ..utils import get_company_types_from_groups

from ..models import STATE_TYPE_CONFIRM, LkpItem, TblCompanyCommitmentDetail, TblCompanyCommitmentMaster, TblCompanyCommitmentSchedular

commitment_all_qs = TblCompanyCommitmentMaster.objects.prefetch_related("company")
commitment_confirmed_qs = commitment_all_qs.filter(state=STATE_TYPE_CONFIRM)

item_none = LkpItem.objects.none()
item_all_qs = LkpItem.objects.all()

class TblCompanyCommitmentAdminForm(ModelForm):
    # company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), label=_("company"))
    class Meta:
        model = TblCompanyCommitmentMaster
        fields = ["company","license","currency","note","state"] 
        
class TblCompanyAddCommitmentForm(TblCompanyCommitmentAdminForm):
    user = None
    layout = [["company","license","currency"],["note"]]
    class Meta:
        model = TblCompanyCommitmentMaster     
        fields = ["company","license","currency","note"] 
        widgets = {}

    def __init__(self, *args,company_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        if company_id:
            company = TblCompanyProduction.objects.get(pk=company_id,company_type__in=get_company_types_from_groups(self.user))
            self.fields["company"].queryset = TblCompanyProduction.objects.filter(id=company.id)
            self.fields["license"].queryset = TblCompanyProductionLicense.objects.filter(company__id=company.id)
        else:
            self.fields["company"].queryset = TblCompanyProduction.objects.none()
            self.fields["license"].queryset = TblCompanyProductionLicense.objects.none()

class TblCompanyShowEditCommitmentForm(TblCompanyCommitmentAdminForm):
    user = None
    layout = [["company","license","currency"],["note"]]
    class Meta:
        model = TblCompanyCommitmentMaster     
        fields = ["company","license","currency","note"] 
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('instance') and kwargs['instance'].pk:
            pk = kwargs['instance'].company.id
        
        if pk:
            company = TblCompanyProduction.objects.get(pk=pk,company_type__in=get_company_types_from_groups(self.user))
            self.fields["company"].queryset = TblCompanyProduction.objects.filter(id=company.id)
            self.fields["license"].queryset = TblCompanyProductionLicense.objects.filter(company__id=company.id)
        else:
            self.fields["company"].queryset = TblCompanyProduction.objects.none()
            self.fields["license"].queryset = TblCompanyProductionLicense.objects.none()

class TblCompanyCommitmentDetailForm(ModelForm):
    item = forms.ModelChoiceField(queryset=item_none,disabled=True, label=_("item"))
    company_type = None
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

        self.fields["item"].queryset = item_all_qs.filter(company_type=self.company_type)
        self.fields["item"].disabled = False
    class Meta:
        model = TblCompanyCommitmentDetail     
        fields = ["item","amount_factor"] 
        widgets = {}

class TblCompanyRequestChooseCompanyForm(forms.Form):
    user = None
    layout = [["company",""]]
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.none(), label=_("company"))
    class Meta:
        model = TblCompanyCommitmentMaster      
        fields = ["company"] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = TblCompanyProduction.objects.filter(company_type__in=get_company_types_from_groups(self.user)).order_by("name_ar")
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
