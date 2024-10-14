from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet,ModelChoiceFilter,ChoiceFilter

from company_profile.models import TblCompanyProduction

from ..models import LkpItem, TblCompanyRequestMaster,STATE_TYPE_CHOICES,STATE_TYPE_DRAFT,STATE_TYPE_CONFIRM

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyRequestTable(BaseTable):
    menu_name = "pa:request_show"
    relation_fields = ["commitment","commitment__company"]
    total = tables.Column(verbose_name= _('request_total'),orderable=False)
    sum_of_confirmed_payment = tables.Column(verbose_name= _('payments total'),orderable=False)

    class Meta:
        model = TblCompanyRequestMaster
        template_name = "django_tables2/bootstrap.html"
        fields = ("commitment","from_dt","to_dt","currency","payment_state","total","sum_of_confirmed_payment","state")
        empty_text = _("No records.")        

    def render_commitment(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        return format_html("{}",value)
    
    
class TblCompanyRequestCompanyTable(BaseTable):
    menu_name = "profile:pa_request_show"
    relation_fields = ["commitment","commitment__company"]
    total = tables.Column(verbose_name= _('request_total'))
    sum_of_confirmed_payment = tables.Column(verbose_name= _('payments total'))

    class Meta:
        model = TblCompanyRequestMaster
        template_name = "django_tables2/bootstrap.html"
        fields = ("from_dt","to_dt","currency","total","sum_of_confirmed_payment","payment_state")
        empty_text = _("No records.")        

    def render_from_dt(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

class RequestFilter(FilterSet):
    company = ModelChoiceFilter(queryset=TblCompanyProduction.objects.all(),field_name='commitment__company', label=_('company'))   
    payment_state = ChoiceFilter(choices=TblCompanyRequestMaster.REQUEST_PAYMENT_CHOICES,field_name='payment_state', label=_('payment_state'))   
    state = ChoiceFilter(choices=STATE_TYPE_CHOICES,field_name='state', label=_('record_state'))   
    class Meta:
        model = TblCompanyRequestMaster
        fields = {}
