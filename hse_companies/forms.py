from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from hse_companies.models import TblStateRepresentative


UserModel = get_user_model()

class TblStateRepresentativeForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=('hse_cmpny_state_mngr',)), label=_("user"))

    class Meta:
        model = TblStateRepresentative    
        fields = ["user","name","state"] 
