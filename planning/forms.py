from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import Department

UserModel = get_user_model()

class DepartmentForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=['planning_user',]), label=_("user"))

    class Meta:
        model = Department    
        fields = ["user","name"] 
