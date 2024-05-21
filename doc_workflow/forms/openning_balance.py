from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from ..models import TblCompanyOpenningBalanceDetail, TblCompanyOpenningBalanceMaster

class TblCompanyOpenningBalanceAdminForm(ModelForm):
    class Meta:
        model = TblCompanyOpenningBalanceMaster
        fields = ["company","currency","state"] 
        
class TblCompanyOpenningBalanceForm(TblCompanyOpenningBalanceAdminForm):
    layout = [["company","currency"]]
    class Meta:
        model = TblCompanyOpenningBalanceMaster     
        fields = ["company","currency"] 
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].widget.attrs.update({"class": "select2"})

class TblCompanyOpenningBalanceDetailForm(ModelForm):
    class Meta:
        model = TblCompanyOpenningBalanceDetail     
        fields = ["item","amount"] 
        widgets = {}
