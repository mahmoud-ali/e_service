from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from ..models import TblCompanyRequest,TblCompanyPayment,STATE_TYPE_CONFIRM

class TblCompanyPaymentAdminForm(ModelForm):
    class Meta:
        model = TblCompanyPayment
        fields = ["request","payment_dt","amount","currency","excange_rate"] 
        
class TblCompanyPaymentForm(TblCompanyPaymentAdminForm):
    request = forms.ModelChoiceField(queryset=TblCompanyRequest.objects.filter(state=STATE_TYPE_CONFIRM,payment_state__in=(TblCompanyRequest.REQUEST_PAYMENT_NO_PAYMENT,TblCompanyRequest.REQUEST_PAYMENT_PARTIAL_PAYMENT)), label=_("request"))
    class Meta:
        model = TblCompanyPayment        
        fields = ["request","payment_dt","amount","currency","excange_rate"] 
        widgets = {
            "payment_dt":AdminDateWidget(),
        }
