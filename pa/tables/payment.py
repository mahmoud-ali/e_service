from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import TblCompanyPayment

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyPaymentTable(BaseTable):
    menu_name = "pa:payment_show"
    relation_fields = []

    class Meta:
        model = TblCompanyPayment
        template_name = "django_tables2/bootstrap.html"
        fields = ("request","payment_dt","amount","currency","excange_rate","state")
        empty_text = _("No records.")        
    
    def render_request(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

class PaymentFilter(FilterSet):
    class Meta:
        model = TblCompanyPayment
        fields = {
            "request__commitement__company": ["exact"],
            "request__commitement__item": ["exact"],
            "state": ["exact"],
        }
