from django import forms
from django.utils.translation import gettext_lazy as _

from help_request.models import HelpRecord

class HelpForm(forms.ModelForm):
    class Meta:
        model = HelpRecord
        fields = ['issue_app','issue_url','issue_txt','issue_img']
        widgets = {
            'issue_app':forms.HiddenInput(),
            'issue_url':forms.HiddenInput(),
            'issue_img':forms.HiddenInput(),
            'issue_txt':forms.Textarea(),
        }