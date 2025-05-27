from django import forms
from django.utils.translation import gettext_lazy as _
from gold_travel.models import AppMoveGold
from .models import TransferRelocationFormData

export_qs = AppMoveGold.objects.filter(state=AppMoveGold.STATE_SMRC, form_type=AppMoveGold.FORM_TYPE_GOLD_EXPORT)
reexport_qs = AppMoveGold.objects.filter(state=AppMoveGold.STATE_SMRC, form_type=AppMoveGold.FORM_TYPE_GOLD_REEXPORT)
silver_qs = AppMoveGold.objects.filter(state=AppMoveGold.STATE_SMRC, form_type=AppMoveGold.FORM_TYPE_SILVER_EXPORT)

class ExportTransferRelocationFormDataForm(forms.ModelForm):
    class Meta:
        model = TransferRelocationFormData
        fields = ['form', 'raw_weight', 'allow_count','smrc_file'] #,'attachement_file'
    
    form = forms.ModelChoiceField(
        queryset=export_qs,
        label=_("Move Gold"),
        widget=forms.Select(attrs={'class': 'select2', 'data-placeholder': _('Select SMRC Code')})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['form'].queryset = export_qs

class ReexportTransferRelocationFormDataForm(forms.ModelForm):
    class Meta:
        model = TransferRelocationFormData
        fields = ['form', 'raw_weight', 'allow_count','smrc_file'] #,'attachement_file'
    
    form = forms.ModelChoiceField(
        queryset=reexport_qs,
        label=_("Move Gold"),
        widget=forms.Select(attrs={'class': 'select2', 'data-placeholder': _('Select SMRC Code')})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['form'].queryset = reexport_qs

class SilverTransferRelocationFormDataForm(forms.ModelForm):
    class Meta:
        model = TransferRelocationFormData
        fields = ['form', 'raw_weight', 'allow_count','smrc_file'] #,'attachement_file'
    
    form = forms.ModelChoiceField(
        queryset=silver_qs,
        label=_("Move Gold"),
        widget=forms.Select(attrs={'class': 'select2', 'data-placeholder': _('Select SMRC Code')})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['form'].queryset = silver_qs
