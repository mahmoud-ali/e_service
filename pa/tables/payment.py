from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
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
        fields = ("id","request","payment_dt","amount","currency","excange_rate")
        empty_text = _("No records.")        

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)
    