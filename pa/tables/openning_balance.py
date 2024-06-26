from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import TblCompanyOpenningBalanceMaster

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyOpenningBalanceTable(BaseTable):
    menu_name = "pa:openning_balance_show"
    relation_fields = ["company"]

    class Meta:
        model = TblCompanyOpenningBalanceMaster
        template_name = "django_tables2/bootstrap.html"
        fields = ("company","currency","state")
        empty_text = _("No records.")        

    def render_company(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        return format_html("{}",value)

class OpenningBalanceFilter(FilterSet):
    class Meta:
        model = TblCompanyOpenningBalanceMaster
        fields = {
            "company": ["exact"],
            "state": ["exact"],
        }
