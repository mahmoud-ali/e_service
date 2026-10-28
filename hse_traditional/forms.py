from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from hse_traditional.models import (
    HseTraditionalAccident, HseTraditionalCorrectiveAction,
    HseTraditionalNearMiss, HseTraditionalReport, TblStateRepresentative,
    MonthlyPerformanceReport,
)
from traditional_app.models import LkpSoag

UserModel = get_user_model()

class TblStateRepresentativeForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=('hse_tra_state_employee',)), label=_("user"))

    class Meta:
        model = TblStateRepresentative    
        fields = ["user","name","state"] 

class HseTraditionalCorrectiveActionForm(forms.ModelForm):
    source_report = forms.ModelChoiceField(queryset=HseTraditionalReport.objects.filter(state__gte=HseTraditionalReport.STATE_CONFIRMED), label=_("تقرير شهري"), required=False)
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
                self.fields['source_report'].queryset =  self.fields['source_report'].queryset.filter(source_state = state)
                self.fields['source_accident'].queryset =  self.fields['source_accident'].queryset.filter(source_state = state)
                self.fields['source_near_miss'].queryset =  self.fields['source_near_miss'].queryset.filter(source_state = state)

        else:
            self.fields['source_report'].queryset =  self.fields['source_report'].queryset.filter(source_state = state)
            self.fields['source_accident'].queryset =  self.fields['source_accident'].queryset.filter(source_state = state)
            self.fields['source_near_miss'].queryset =  self.fields['source_near_miss'].queryset.filter(source_state = state)

    class Meta:
        model = HseTraditionalCorrectiveAction
        fields = ["source_report","source_accident","source_near_miss","when","corrective_action",] 
        widgets = {
            'when': forms.DateInput(attrs={'type': 'date'}),
        }


class MonthlyPerformanceReportForm(forms.ModelForm):
    soag = forms.ModelChoiceField(
        queryset=LkpSoag.objects.all(),
        label=_("السوق"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_state = None

        try:
            user_state = self.request.user.hse_tra_state.state
        except:
            pass

        if user_state:
            self.fields['soag'].queryset = LkpSoag.objects.filter(state=user_state)
            if not self.instance.pk:
                self.fields['source_state'].initial = user_state

    def clean(self):
        cleaned_data = super().clean()

        source_state = cleaned_data.get('source_state')
        user_state = None

        try:
            user_state = self.request.user.hse_tra_state.state
        except Exception:
            pass

        if not user_state and not source_state:
            raise forms.ValidationError(
                _("لم يتم اسناد الولاية لمدخل البيانات، يرجى التواصل مع مسؤول النظام لإعداد الولاية الخاصة بك.")
            )

        soag = cleaned_data.get('soag')
        effective_state = user_state or source_state
        if soag and effective_state and hasattr(soag, 'state') and soag.state:
            if soag.state != effective_state:
                raise forms.ValidationError(
                    _("السوق المختار لا ينتمي إلى الولاية المحددة، يرجى اختيار سوق من ولايتك.")
                )

        return cleaned_data

    class Meta:
        model = MonthlyPerformanceReport
        fields = ['year', 'month', 'source_state', 'soag', 'main_activities',
                  'karta_relocated_ton', 'karta_stacked_ton', 'karta_processed_ton']