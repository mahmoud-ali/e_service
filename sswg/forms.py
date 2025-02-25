from django import forms
from django.utils.translation import gettext_lazy as _
from gold_travel.models import AppMoveGold
from .models import TransferRelocationFormData

class TransferRelocationFormDataForm(forms.ModelForm):
    class Meta:
        model = TransferRelocationFormData
        fields = ['form', 'raw_weight', 'allow_count','smrc_file'] #,'attachement_file'
    
    form = forms.ModelChoiceField(
        queryset=AppMoveGold.objects.filter(state=AppMoveGold.STATE_SMRC),
        label=_("Move Gold"),
        widget=forms.Select(attrs={'class': 'select2', 'data-placeholder': _('Select SMRC Code')})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['form'].queryset = AppMoveGold.objects.filter(state=AppMoveGold.STATE_SMRC)
