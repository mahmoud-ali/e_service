from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import TblCompanyCommitmentSchedular,STATE_TYPE_CHOICES,STATE_TYPE_DRAFT,STATE_TYPE_CONFIRM

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyCommitmentScheduleTable(BaseTable):
    menu_name = "pa:commitment_schedule_show"
    relation_fields = ["commitment"]

    class Meta:
        model = TblCompanyCommitmentSchedular
        template_name = "django_tables2/bootstrap.html"
        fields = ("commitment","request_interval","request_next_interval_dt","request_auto_confirm","state")
        empty_text = _("No records.")        

    def render_commitment(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

class CommitmentScheduleFilter(FilterSet):
    class Meta:
        model = TblCompanyCommitmentSchedular
        fields = {
            "commitment": ["exact"],
            "request_interval": ["exact"],
        }
