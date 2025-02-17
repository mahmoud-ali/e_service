from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompanyProduction,TblCompany

from .models import CompanyProductionTask, Department

UserModel = get_user_model()

company_none = TblCompanyProduction.objects.none()
company_all_qs = TblCompanyProduction.objects.all()

class DepartmentForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=['planning_user',]), label=_("user"))

    class Meta:
        model = Department    
        fields = ["user","name"] 

class CompanyProductionEntagTaskForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=company_none,disabled=True, label=_("company"))
    company_types = [TblCompany.COMPANY_TYPE_ENTAJ,TblCompany.COMPANY_TYPE_MOKHALFAT]
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

        self.fields["company"].queryset = company_all_qs.filter(company_type__in=self.company_types)
            
        self.fields["company"].disabled = False
    class Meta:
        model = CompanyProductionTask
        fields = ["company","total_weight",]
        widgets = {}

class CompanyProductionSageerTaskForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=company_none,disabled=True, label=_("company"))
    company_types = [TblCompany.COMPANY_TYPE_SAGEER]
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

        self.fields["company"].queryset = company_all_qs.filter(company_type__in=self.company_types)
            
        self.fields["company"].disabled = False
    class Meta:
        model = CompanyProductionTask
        fields = ["company","total_weight",]
        widgets = {}
