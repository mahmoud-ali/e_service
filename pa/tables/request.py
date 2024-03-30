from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet,ModelChoiceFilter,ChoiceFilter

from company_profile.models import TblCompanyProduction

from ..models import LkpItem, TblCompanyRequest,STATE_TYPE_CHOICES,STATE_TYPE_DRAFT,STATE_TYPE_CONFIRM

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyRequestTable(BaseTable):
    menu_name = "pa:request_show"
    relation_fields = ["commitement","commitement__company","commitement__item"]

    class Meta:
        model = TblCompanyRequest
        template_name = "django_tables2/bootstrap.html"
        fields = ("commitement","from_dt","to_dt","amount","currency","payment_state","state")
        empty_text = _("No records.")        

    def render_commitement(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        return format_html("{}",value)

class RequestFilter(FilterSet):
    company = ModelChoiceFilter(queryset=TblCompanyProduction.objects.all(),field_name='commitement__company', label=_('company'))   
    item = ModelChoiceFilter(queryset=LkpItem.objects.all(),field_name='commitement__item', label=_('item'))   
    payment_state = ChoiceFilter(choices=TblCompanyRequest.REQUEST_PAYMENT_CHOICES,field_name='payment_state', label=_('payment_state'))   
    state = ChoiceFilter(choices=STATE_TYPE_CHOICES,field_name='state', label=_('record_state'))   
    class Meta:
        model = TblCompanyRequest
        fields = {}
