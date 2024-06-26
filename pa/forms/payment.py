from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from bootstrap_datepicker_plus.widgets import DatePickerInput

from ..models import TblCompanyRequestMaster,TblCompanyPaymentMaster,STATE_TYPE_CONFIRM

request_all_qs = TblCompanyRequestMaster.objects.prefetch_related("commitment","commitment__company")

class TblCompanyPaymentAdminForm(ModelForm):
    class Meta:
        model = TblCompanyPaymentMaster
        fields = ["request","payment_dt","currency","exchange_rate","exchange_attachement_file","state"] 

    def __init__(self, *args,request_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if request_id:
            self.fields["request"].queryset = request_all_qs.filter(id=request_id)

class TblCompanyPaymentShowEditForm(TblCompanyPaymentAdminForm):
    layout = [["request","",""],["payment_dt","",""],["currency","exchange_rate","exchange_attachement_file"]]
    request = forms.ModelChoiceField(queryset=request_all_qs,disabled=True, label=_("request"))

    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)
        pk = None

        if kwargs.get('instance') and kwargs['instance'].pk:
            pk = kwargs['instance'].request.id
        
        if pk:
            self.fields["request"].queryset = request_all_qs.filter(id=pk)

    class Meta:
        model = TblCompanyPaymentMaster
        fields = ["request","payment_dt","currency","exchange_rate","exchange_attachement_file"] 
        widgets = {
            "payment_dt":DatePickerInput(),
        }

class TblCompanyPaymentAddForm(TblCompanyPaymentAdminForm):
    layout = [["request","",""],["payment_dt","",""],["currency","exchange_rate","exchange_attachement_file"]]
    request = forms.ModelChoiceField(queryset=request_all_qs.filter(state=STATE_TYPE_CONFIRM,payment_state__in=(TblCompanyRequestMaster.REQUEST_PAYMENT_NO_PAYMENT,TblCompanyRequestMaster.REQUEST_PAYMENT_PARTIAL_PAYMENT)), label=_("request"))
    class Meta:
        model = TblCompanyPaymentMaster
        fields = ["request","payment_dt","currency","exchange_rate","exchange_attachement_file"] 
        widgets = {
            "payment_dt":DatePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["request"].widget.attrs.update({"class": "select2"})

class TblCompanyPaymentChooseRequestForm(forms.Form):
    layout = [["request",""]]
    request = forms.ModelChoiceField(queryset=request_all_qs.filter(state=STATE_TYPE_CONFIRM,payment_state__in=(TblCompanyRequestMaster.REQUEST_PAYMENT_NO_PAYMENT,TblCompanyRequestMaster.REQUEST_PAYMENT_PARTIAL_PAYMENT)), label=_("request"))
    class Meta:
        model = TblCompanyRequestMaster      
        fields = ["request"] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["request"].widget.attrs.update({"class": "select2"})
