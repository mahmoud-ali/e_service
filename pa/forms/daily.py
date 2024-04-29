from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import AdminDateWidget

from company_profile.models import TblCompanyProduction
from pa.models import CURRENCY_TYPE_CHOICES

class PaDailyForm(forms.Form):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(),label=_("company"),required=False,empty_label=_("all"))
    currency = forms.ChoiceField(choices=CURRENCY_TYPE_CHOICES,label=_("currency"))
    from_dt = forms.DateField(label=_("from_dt"),widget=AdminDateWidget)
    to_dt = forms.DateField(label=_("to_dt"),widget=AdminDateWidget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].widget.attrs.update({"class": "select2"})
