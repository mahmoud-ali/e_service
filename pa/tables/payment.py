from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet,ModelChoiceFilter,ChoiceFilter

from company_profile.models import TblCompanyProduction
from ..models import TblCompanyPaymentMaster,LkpItem,STATE_TYPE_CHOICES,STATE_TYPE_DRAFT,STATE_TYPE_CONFIRM

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyPaymentTable(BaseTable):
    menu_name = "pa:payment_show"
    relation_fields = ["request","request__commitment","request__commitment__company"]
    total = tables.Column(verbose_name= _('اجمالي السداد'),orderable=False)
    total_request_currency = tables.Column(verbose_name= _('اجمالي السداد بعملة المطالبة'),orderable=False)
    total_sdg = tables.Column(verbose_name= _('اجمالي السداد بالجنيه'),orderable=False)

    class Meta:
        model = TblCompanyPaymentMaster
        template_name = "django_tables2/bootstrap.html"
        fields = ("request","payment_dt","currency","exchange_rate","total_request_currency","total_sdg","state")
        empty_text = _("No records.")        
    
    def render_request(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        return format_html("{}",value)

class PaymentFilter(FilterSet):
    company = ModelChoiceFilter(queryset=TblCompanyProduction.objects.all(),field_name='request__commitment__company', label=_('company'))   
    state = ChoiceFilter(choices=STATE_TYPE_CHOICES,field_name='state', label=_('record_state'))   
    class Meta:
        model = TblCompanyPaymentMaster
        fields = {}
