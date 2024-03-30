from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from ..models import TblCompanyCommitment,TblCompanyRequest,STATE_TYPE_CONFIRM

commitement_all_qs = TblCompanyCommitment.objects.prefetch_related("company","item")

class TblCompanyRequestAdminForm(ModelForm):
    class Meta:
        model = TblCompanyRequest
        fields = ["commitement","from_dt","to_dt","amount","currency"] 
        
class TblCompanyRequestForm(TblCompanyRequestAdminForm):
    commitement = forms.ModelChoiceField(queryset=commitement_all_qs.filter(state=STATE_TYPE_CONFIRM).order_by("company"), label=_("commitement"))
    class Meta:
        model = TblCompanyRequest        
        fields = ["commitement","from_dt","to_dt","amount","currency"] 
        widgets = {
            "from_dt":AdminDateWidget(),
            "to_dt":AdminDateWidget(),
        }
