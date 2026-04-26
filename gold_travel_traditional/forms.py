from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from gold_travel_traditional.models import AppMoveGoldTraditional, GoldTravelTraditionalUser, GoldTravelTraditionalUserJihatAlaisdar, GoldTravelTraditionalUserJihatTarhil, LkpJihatAlaisdar, LkpJihatAltarhil

UserModel = get_user_model()

class GoldTravelTraditionalUserForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=['gold_travel_traditional_state',]), label=_("user"))

    class Meta:
        model = GoldTravelTraditionalUser    
        fields = ["user","name","state",] 

class GoldTravelTraditionalUserJihatAlaisdarForm(forms.ModelForm):
    jihat_alaisdar = forms.ModelChoiceField(queryset=LkpJihatAlaisdar.objects.none(), label=_("جهة الإصدار"))
    allowed_state = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.filter(state=self.allowed_state)

    class Meta:
        model = GoldTravelTraditionalUserJihatAlaisdar   
        fields = ["jihat_alaisdar",] 

class GoldTravelTraditionalUserJihatTarhilForm(forms.ModelForm):
    wijhat_altarhil = forms.ModelChoiceField(queryset=LkpJihatAltarhil.objects.none(), label=_("جهة الوصول"))
    allowed_state = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.filter(state=self.allowed_state)

    class Meta:
        model = GoldTravelTraditionalUserJihatTarhil   
        fields = ["wijhat_altarhil",] 

class AppMoveGoldTraditionalAddForm(forms.ModelForm):
    jihat_alaisdar = forms.ModelChoiceField(queryset=LkpJihatAlaisdar.objects.none(), label=_("جهة الإصدار"))
    wijhat_altarhil = forms.ModelChoiceField(queryset=LkpJihatAltarhil.objects.none(), label=_("جهة الوصول"))
    almushtari_name = forms.CharField(label=_("almushtari_name"), max_length=150, disabled=True, required=False)
    
    user = None
    allowed_state = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.user: # and not self.user.is_superuser
            try:
                gold_user = self.user.gold_travel_traditional
                self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.filter(
                    id__in=gold_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True)
                )
                self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.filter(
                    id__in=gold_user.goldtraveltraditionaluserjihattarhil_set.values_list('wijhat_altarhil', flat=True)
                )
            except:
                self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.none()
                self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.none()
        else:
            self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.all()
            self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.all()

    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["issue_date","almustafid_name","almustafid_phone","almustafid_identity_type","almustafid_identity","jihat_alaisdar","wijhat_altarhil","state","source_state"] 
        
class AppMoveGoldTraditionalSoldForm(forms.ModelForm):
    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["almushtari_name",] 

class AppMoveGoldTraditionalRenewForm(forms.ModelForm):
    jihat_alaisdar = forms.ModelChoiceField(queryset=LkpJihatAlaisdar.objects.none(), label=_("جهة الإصدار"))
    wijhat_altarhil = forms.ModelChoiceField(queryset=LkpJihatAltarhil.objects.none(), label=_("جهة الوصول"))

    user = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.user and not self.user.is_superuser:
            try:
                gold_user = self.user.gold_travel_traditional
                self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.filter(
                    id__in=gold_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True)
                )
                self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.filter(
                    id__in=gold_user.goldtraveltraditionaluserjihattarhil_set.values_list('wijhat_altarhil', flat=True)
                )
            except:
                self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.none()
                self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.none()
        else:
            self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.all()
            self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.all()

    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["code","issue_date","almustafid_name","almustafid_phone","almustafid_identity_type","almustafid_identity","jihat_alaisdar","wijhat_altarhil",] 
        # widgets = {
        #     'issue_date': admin.widgets.AdminDateWidget(),
        #     'jihat_alaisdar': forms.Select(),
        #     'gold_weight_in_gram': forms.TextInput(),
        # }
