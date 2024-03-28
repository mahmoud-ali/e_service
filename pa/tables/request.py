from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import TblCompanyRequest,STATE_TYPE_CHOICES,STATE_TYPE_DRAFT,STATE_TYPE_CONFIRM

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyRequestTable(BaseTable):
    menu_name = "pa:request_show"
    menu_confirm_name = "pa:request_confirm"
    relation_fields = []

    class Meta:
        model = TblCompanyRequest
        template_name = "django_tables2/bootstrap.html"
        fields = ("commitement","from_dt","to_dt","amount","currency","payment_state","state")
        empty_text = _("No records.")        

    def render_commitement(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        if record.state == STATE_TYPE_DRAFT:
            return format_html('{} <br /> <a class="btn btn-success" href={}>{}</a>',value,reverse_lazy(self.menu_confirm_name,args=(record.id,)),_("confirm_btn"))
        else:
            return format_html("{}",value)

class RequestFilter(FilterSet):
    class Meta:
        model = TblCompanyRequest
        fields = {
            "commitement__company": ["exact"],
            "commitement__item": ["exact"],
            "payment_state": ["exact"],
            "state": ["exact"],
        }
