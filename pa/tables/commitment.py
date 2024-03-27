from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import TblCompanyCommitment

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyCommitmentTable(BaseTable):
    menu_name = "pa:commitment_show"
    relation_fields = []

    class Meta:
        model = TblCompanyCommitment
        template_name = "django_tables2/bootstrap.html"
        fields = ("company","item","amount","currency")
        empty_text = _("No records.")        

    def render_company(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

class CommitmentFilter(FilterSet):
    class Meta:
        model = TblCompanyCommitment
        fields = {"company": ["exact"],"item": ["exact"]}
