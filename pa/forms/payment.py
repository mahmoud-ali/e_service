from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompanyProduction

from ..models import TblCompanyPayment,LkpItem

class TblCompanyPaymentAdminForm(ModelForm):
    class Meta:
        model = TblCompanyPayment
        fields = ["request","payment_dt","amount","currency","excange_rate"] 
        
class TblCompanyPaymentForm(TblCompanyPaymentAdminForm):
    # company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(), label=_("company"))
    # item = forms.ModelChoiceField(queryset=LkpItem.objects.filter(id=-1), label=_("item"))
    class Meta:
        model = TblCompanyPayment        
        # fields = ["company","item","request","payment_dt","amount","currency","excange_rate"] 
        fields = ["request","payment_dt","amount","currency","excange_rate"] 
        widgets = {
            "payment_dt":AdminDateWidget(),
        }
