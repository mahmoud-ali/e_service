from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from gold_travel_traditional.models import AppMoveGoldTraditional, GoldTravelTraditionalUser, LkpJihatAlaisdar, LkpSoag

UserModel = get_user_model()

class GoldTravelTraditionalUserForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=['gold_travel_traditional_state',]), label=_("user"))

    class Meta:
        model = GoldTravelTraditionalUser    
        fields = ["user","name","state",] 

class AppMoveGoldTraditionalAddForm(forms.ModelForm):
    jihat_alaisdar = forms.ModelChoiceField(queryset=LkpJihatAlaisdar.objects.none(), label=_("jihat_alaisdar"))
    # wijhat_altarhil = forms.ModelChoiceField(queryset=LkpSoag.objects.none(), label=_("wijhat altarhil"))
    almushtari_name = forms.CharField(max_length=150, disabled=True)
    allowed_state = None
    allowed_soug_list = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.filter(state=self.allowed_state)
        # self.fields["wijhat_altarhil"].queryset = LkpSoag.filter(state=self.allowed_state,id__in=self.allowed_soug_list)

    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["code","issue_date","gold_weight_in_gram","almustafid_name","almustafid_phone","jihat_alaisdar","wijhat_altarhil","muharir_alaistimara","almushtari_name","state","source_state"] 
        
class AppMoveGoldTraditionalSoldForm(forms.ModelForm):
    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["almushtari_name",] 

class AppMoveGoldTraditionalRenewForm(forms.ModelForm):
    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["code","issue_date","gold_weight_in_gram","almustafid_name","almustafid_phone","jihat_alaisdar","wijhat_altarhil","muharir_alaistimara",] 
        # widgets = {
        #     'issue_date': admin.widgets.AdminDateWidget(),
        #     'jihat_alaisdar': forms.Select(),
        #     'gold_weight_in_gram': forms.TextInput(),
        # }
