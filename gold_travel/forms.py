from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from gold_travel.models import TblStateRepresentative

UserModel = get_user_model()

class TblStateRepresentativeForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=('gold_travel_state','gold_travel_ssmo')), label=_("user"))
    # def __init__(self, *args, **kwargs):        
    #     super().__init__(*args, **kwargs)

    class Meta:
        model = TblStateRepresentative    
        fields = ["user","name","state","authority"] 
