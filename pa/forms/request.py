from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _

from ..models import TblCompanyCommitment,TblCompanyRequest,STATE_TYPE_CONFIRM

commitement_all_qs = TblCompanyCommitment.objects.prefetch_related("company","item")
commitement_confirmed_qs = commitement_all_qs.filter(state=STATE_TYPE_CONFIRM)

class TblCompanyRequestAdminForm(ModelForm):
    class Meta:
        model = TblCompanyRequest
        fields = ["commitement","from_dt","to_dt","amount","currency"] 
        
class TblCompanyRequestShowEditForm(TblCompanyRequestAdminForm):
    commitement = forms.ModelChoiceField(queryset=None,disabled=True, label=_("commitement"))

    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)
        pk = None

        if kwargs.get('instance') and kwargs['instance'].pk:
            pk = kwargs['instance'].commitement.id
        
        if pk:
            self.fields["commitement"].queryset = commitement_all_qs.filter(id=pk)

    class Meta:
        model = TblCompanyRequest        
        fields = ["commitement","from_dt","to_dt","amount","currency"] 
        widgets = {
            "from_dt":AdminDateWidget(),
            "to_dt":AdminDateWidget(),
        }

class TblCompanyRequestAddForm(TblCompanyRequestAdminForm):
    commitement = forms.ModelChoiceField(queryset=commitement_confirmed_qs.filter(request_interval=TblCompanyCommitment.INTERVAL_TYPE_MANUAL).order_by("company"), label=_("commitement"))
    class Meta:
        model = TblCompanyRequest        
        fields = ["commitement","from_dt","to_dt","amount","currency"] 
        widgets = {
            "from_dt":AdminDateWidget(),
            "to_dt":AdminDateWidget(),
        }

