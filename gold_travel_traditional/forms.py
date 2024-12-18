from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from gold_travel_traditional.models import AppMoveGoldTraditional, GoldTravelTraditionalUser, GoldTravelTraditionalUserDetail, LkpJihatAlaisdar, LkpSoag

UserModel = get_user_model()

class GoldTravelTraditionalUserForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=['gold_travel_traditional_state',]), label=_("user"))

    class Meta:
        model = GoldTravelTraditionalUser    
        fields = ["user","name","state",] 

class GoldTravelTraditionalUserDetailForm(forms.ModelForm):
    soug = forms.ModelChoiceField(queryset=LkpSoag.objects.none(), label=_("user"))
    allowed_state = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["soug"].queryset = LkpSoag.objects.filter(state=self.allowed_state)

    class Meta:
        model = GoldTravelTraditionalUserDetail   
        fields = ["soug",] 

class AppMoveGoldTraditionalAddForm(forms.ModelForm):
    jihat_alaisdar = forms.ModelChoiceField(queryset=LkpJihatAlaisdar.objects.none(), label=_("jihat_alaisdar"))
    # wijhat_altarhil = forms.ModelChoiceField(queryset=LkpSoag.objects.none(), label=_("wijhat altarhil"))
    almushtari_name = forms.CharField(label=_("almushtari_name"), max_length=150, disabled=True, required=False)
    allowed_state = None
    allowed_soug_list = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.filter(state=self.allowed_state)
        if hasattr(self.fields,"almushtari_name"):
            self.fields["almushtari_name"].disabled = True
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
