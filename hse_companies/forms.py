from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from hse_companies.models import (
    TblStateRepresentative,
    TblCompanyEvaluationSession,
    TblCompanyEvaluationEnvironment,
    TblCompanyEvaluationSafety,
    TblCompanyEvaluationGeneral
)
from company_profile.models import TblCompanyProduction, LkpState, LkpLocality

UserModel = get_user_model()

class TblStateRepresentativeForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=('hse_cmpny_state_mngr',)), label=_("user"))

    class Meta:
        model = TblStateRepresentative    
        fields = ["user","name","state"]


class HseEvaluationSessionForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all().order_by('name_ar'), label=_("company"), widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    state = forms.ModelChoiceField(queryset=LkpState.objects.all().order_by('name'), label=_("state"), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    locality = forms.ModelChoiceField(queryset=LkpLocality.objects.all().order_by('name'), label=_("locality"), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    evaluation_date = forms.DateField(label=_("تاريخ التقييم"), widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}))

    class Meta:
        model = TblCompanyEvaluationSession
        fields = ['company', 'state', 'locality', 'evaluation_date']

class HseEnvironmentEvaluationForm(forms.ModelForm):
    class Meta:
        model = TblCompanyEvaluationEnvironment
        exclude = ['session', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class HseSafetyEvaluationForm(forms.ModelForm):
    class Meta:
        model = TblCompanyEvaluationSafety
        exclude = ['session', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class HseGeneralEvaluationForm(forms.ModelForm):
    class Meta:
        model = TblCompanyEvaluationGeneral
        exclude = ['session', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
