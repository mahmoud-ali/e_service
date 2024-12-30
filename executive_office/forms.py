from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from executive_office.models import Contact

UserModel = get_user_model()


class ContactForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=['gold_travel_traditional_state',]), label=_("user"))

    class Meta:
        model = Contact
        fields = ["user","name",] 
