from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from dal import autocomplete

from company_profile.models import TblCompanyProduction,TblCompany
from executive_office.models import Contact, InboxCompany

UserModel = get_user_model()

company_emtiaz_qs = TblCompanyProduction.objects.filter(company_type=TblCompany.COMPANY_TYPE_EMTIAZ)

class ContactForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=['gold_travel_traditional_state',]), label=_("user"))

    class Meta:
        model = Contact
        fields = ["user","name",] 

class InboxCompanyForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=company_emtiaz_qs,
        label=_("company"), 
        widget=autocomplete.ModelSelect2(url='admin:lkp_company_list'),
    )

    class Meta:
        model = InboxCompany
        fields = ["company"] 
