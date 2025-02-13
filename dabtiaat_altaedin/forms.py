from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from dabtiaat_altaedin.models import TblStateRepresentative2

UserModel = get_user_model()

class TblStateRepresentativeForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=('dabtiaat_altaedin_state',)), label=_("user"))
    class Meta:
        model = TblStateRepresentative2
        fields = ["user","name","state","authority"] 
