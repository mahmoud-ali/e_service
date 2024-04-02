from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import AdminDateWidget

from company_profile.models import TblCompanyProduction

class PaDailyForm(forms.Form):
    company = forms.ModelChoiceField(queryset=TblCompanyProduction.objects.all(),label=_("company"))
    from_dt = forms.DateField(label=_("from_dt"),widget=AdminDateWidget)
    to_dt = forms.DateField(label=_("to_dt"),widget=AdminDateWidget)
