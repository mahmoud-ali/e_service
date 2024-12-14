from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from gold_travel_traditional.models import AppMoveGoldTraditional

# UserModel = get_user_model()

class AppMoveGoldTraditionalSoldForm(forms.ModelForm):
    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["almushtari_name",] 

class AppMoveGoldTraditionalRenewForm(forms.ModelForm):
    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["code","issue_date","muharir_alaistimara","almustafid_name","almustafid_phone","jihat_alaisdar","wijhat_altarhil","gold_weight_in_gram",] 

