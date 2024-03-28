from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import TblCompanyPayment,STATE_TYPE_CHOICES,STATE_TYPE_DRAFT,STATE_TYPE_CONFIRM

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyPaymentTable(BaseTable):
    menu_name = "pa:payment_show"
    menu_confirm_name = "pa:payment_confirm"
    relation_fields = []

    class Meta:
        model = TblCompanyPayment
        template_name = "django_tables2/bootstrap.html"
        fields = ("request","payment_dt","amount","currency","excange_rate","state")
        empty_text = _("No records.")        
    
    def render_request(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        if record.state == STATE_TYPE_DRAFT:
            return format_html('{} <br /> <a class="btn btn-success" href={}>{}</a>',value,reverse_lazy(self.menu_confirm_name,args=(record.id,)),_("confirm_btn"))
        else:
            return format_html("{}",value)

class PaymentFilter(FilterSet):
    class Meta:
        model = TblCompanyPayment
        fields = {
            "request__commitement__company": ["exact"],
            "request__commitement__item": ["exact"],
            "state": ["exact"],
        }
