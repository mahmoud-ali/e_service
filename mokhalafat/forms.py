from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from mokhalafat.models import AppMokhalafat, AppChemicalMaterialsViolation, ChemicalViolationStateRepresentative

UserModel = get_user_model()


class AppMokhalafatAdminForm(forms.ModelForm):
    class Meta:
        model = AppMokhalafat
        fields = ['code','date','aism_almukhalafa','wasf_almukhalafa','tahlil_almukhalafa']
        widgets = {
            "wasf_almukhalafa": forms.Textarea,
            "tahlil_almukhalafa": forms.Textarea,
        }


class AppChemicalMaterialsViolationForm(forms.ModelForm):
    class Meta:
        model = AppChemicalMaterialsViolation
        fields = '__all__'
        widgets = {
            "location_details": forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            "owner_statements": forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }


class ChemicalViolationStateRepresentativeForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=UserModel.objects.filter(
            groups__name='mokhalafat_kimyaeya_state'
        ),
        label=_("المستخدم")
    )

    class Meta:
        model = ChemicalViolationStateRepresentative
        fields = ["user", "name", "state"]
