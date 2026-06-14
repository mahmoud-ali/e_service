from django import forms

from mokhalafat.models import AppMokhalafat, AppChemicalMaterialsViolation
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


