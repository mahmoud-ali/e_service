from django import forms

from mokhalafat.models import AppMokhalafat
class AppMokhalafatAdminForm(forms.ModelForm):
    class Meta:
        model = AppMokhalafat
        fields = ['code','date','aism_almukhalafa','wasf_almukhalafa','tahlil_almukhalafa']
        widgets = {
            "wasf_almukhalafa": forms.Textarea,
            "tahlil_almukhalafa": forms.Textarea,
        }

