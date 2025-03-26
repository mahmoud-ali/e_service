from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from hse_traditional.models import HseTraditionalAccident, HseTraditionalCorrectiveAction, HseTraditionalNearMiss, TblStateRepresentative

UserModel = get_user_model()

class TblStateRepresentativeForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=('hse_tra_state_employee',)), label=_("user"))

    class Meta:
        model = TblStateRepresentative    
        fields = ["user","name","state"] 

class HseTraditionalCorrectiveActionForm(forms.ModelForm):
    source_accident = forms.ModelChoiceField(queryset=HseTraditionalAccident.objects.filter(state__gte=HseTraditionalAccident.STATE_CONFIRMED), label=_("source_accident"), required=False)
    source_near_miss = forms.ModelChoiceField(queryset=HseTraditionalNearMiss.objects.filter(state__gte=HseTraditionalNearMiss.STATE_CONFIRMED), label=_("source_near_miss"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        state = None

        try:
            state = self.request.user.hse_tra_state.state
        except:
            pass

        
        if kwargs.get('instance') and kwargs['instance'].pk:
            if kwargs['instance'].state in [HseTraditionalCorrectiveAction.STATE_DRAFT,HseTraditionalCorrectiveAction.STATE_CONFIRMED1]:
                self.fields['source_accident'].queryset =  self.fields['source_accident'].queryset.filter(source_state = state)
                self.fields['source_near_miss'].queryset =  self.fields['source_near_miss'].queryset.filter(source_state = state)

        else:
            self.fields['source_accident'].queryset =  self.fields['source_accident'].queryset.filter(source_state = state)
            self.fields['source_near_miss'].queryset =  self.fields['source_near_miss'].queryset.filter(source_state = state)

    class Meta:
        model = HseTraditionalCorrectiveAction

    class Meta:
        model = HseTraditionalCorrectiveAction
        fields = ["source_accident","source_near_miss","corrective_action"] 