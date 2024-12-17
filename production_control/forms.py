from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from dal import autocomplete

from company_profile.models import TblCompanyProduction

from .models import GoldProductionForm, GoldProductionFormAlloy, GoldProductionUser, GoldProductionUserDetail, GoldShippingForm, GoldShippingFormAlloy, LkpMoragib

UserModel = get_user_model()

company_none = TblCompanyProduction.objects.none()
company_all_qs = TblCompanyProduction.objects.all()

alloy_none = GoldProductionFormAlloy.objects.none()
alloy_all_qs = GoldProductionFormAlloy.objects.all()

class MoragibForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=('production_control_auditor',)), label=_("user"))
    class Meta:
        model = LkpMoragib    
        fields = ["company_type","user","name",] 

class GoldProductionUserForm(forms.ModelForm):
    # user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=('production_control_auditor',)), label=_("user"))
    class Meta:
        model = GoldProductionUser    
        fields = ["moragib"] #"user","name",

class TblCompanyProductionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return TblCompanyProduction.objects.none()

        qs = TblCompanyProduction.objects.all()

        if self.q:
            qs = qs.filter(name_ar__contains=self.q) | qs.filter(name_en__contains=self.q)

        return qs
    
class GoldProductionUserDetailForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=company_none,
        disabled=True, 
        label=_("company"), 
        widget=autocomplete.ModelSelect2(url='admin:lkp_company_list'),
    )
    company_types = []
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

        self.fields["company"].queryset = company_all_qs.filter(company_type__in=self.company_types)
        self.fields["company"].disabled = False
    class Meta:
        model = GoldProductionUserDetail
        fields = ["company"] 

class GoldProductionFormForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=company_none,disabled=True, label=_("company"))
    company_list = []
    company_types = []
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

        if len(self.company_list) > 0:
            self.fields["company"].queryset = company_all_qs.filter(id__in=self.company_list)
        else:
            self.fields["company"].queryset = company_all_qs.filter(company_type__in=self.company_types)
            
        self.fields["company"].disabled = False
    class Meta:
        model = GoldProductionForm     
        fields = ["company","date","form_no","alloy_jaf","alloy_khabath","alloy_remaind","gold_production_form_file","gold_production_3hda_file"]
        widgets = {}

class GoldShippingFormForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=company_none,disabled=True, label=_("company"))
    company_list = []
    company_types = []
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

        if len(self.company_list) > 0:
            self.fields["company"].queryset = company_all_qs.filter(id__in=self.company_list)
        else:
            self.fields["company"].queryset = company_all_qs.filter(company_type__in=self.company_types)
            
        self.fields["company"].disabled = False
    class Meta:
        model = GoldShippingForm     
        fields = ["company","date","form_no","attachement_file"]
        widgets = {}

class GoldShippingFormAlloyForm(forms.ModelForm):
    alloy_serial_no = forms.ModelChoiceField(queryset=alloy_none,disabled=True, label=_("alloy_serial_no"))
    master_id = None
    company_ids = None
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

        self.fields["alloy_serial_no"].queryset = alloy_all_qs.filter(master__company__id__in=self.company_ids,alloy_shipped=False)
        if self.master_id:
            self.fields["alloy_serial_no"].queryset |= alloy_all_qs.filter(id__in=GoldShippingFormAlloy.objects.filter(master=self.master_id).values_list('alloy_serial_no'))

        self.fields["alloy_serial_no"].disabled = False
    class Meta:
        model = GoldShippingFormAlloy
        fields = ["alloy_serial_no"] #,"alloy_weight"
        widgets = {}
