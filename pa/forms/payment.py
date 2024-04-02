from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from ..models import TblCompanyRequest,TblCompanyPayment,STATE_TYPE_CONFIRM

request_all_qs = TblCompanyRequest.objects.prefetch_related("commitement","commitement__company","commitement__item")

class TblCompanyPaymentAdminForm(ModelForm):
    class Meta:
        model = TblCompanyPayment
        fields = ["request","payment_dt","amount","currency","exchange_rate"] 
        
class TblCompanyPaymentShowEditForm(TblCompanyPaymentAdminForm):
    request = forms.ModelChoiceField(queryset=request_all_qs,disabled=True, label=_("request"))

    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)
        pk = None

        if kwargs.get('instance') and kwargs['instance'].pk:
            pk = kwargs['instance'].request.id
        
        if pk:
            self.fields["request"].queryset = request_all_qs.filter(id=pk)

    class Meta:
        model = TblCompanyPayment        
        fields = ["request","payment_dt","amount","currency","exchange_rate"] 
        widgets = {
            "payment_dt":AdminDateWidget(),
        }

class TblCompanyPaymentAddForm(TblCompanyPaymentAdminForm):
    request = forms.ModelChoiceField(queryset=request_all_qs.filter(state=STATE_TYPE_CONFIRM,payment_state__in=(TblCompanyRequest.REQUEST_PAYMENT_NO_PAYMENT,TblCompanyRequest.REQUEST_PAYMENT_PARTIAL_PAYMENT)), label=_("request"))
    class Meta:
        model = TblCompanyPayment        
        fields = ["request","payment_dt","amount","currency","exchange_rate"] 
        widgets = {
            "payment_dt":AdminDateWidget(),
        }
