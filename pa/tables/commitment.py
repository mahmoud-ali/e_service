from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import TblCompanyCommitment,STATE_TYPE_CHOICES,STATE_TYPE_DRAFT,STATE_TYPE_CONFIRM

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyCommitmentTable(BaseTable):
    menu_name = "pa:commitment_show"
    menu_confirm_name = "pa:commitment_confirm"
    relation_fields = []

    class Meta:
        model = TblCompanyCommitment
        template_name = "django_tables2/bootstrap.html"
        fields = ("company","item","amount","currency","state")
        empty_text = _("No records.")        

    def render_company(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        if record.state == STATE_TYPE_DRAFT:
            return format_html('{} <br /> <a class="btn btn-success" href={}>{}</a>',value,reverse_lazy(self.menu_confirm_name,args=(record.id,)),_("confirm_btn"))
        else:
            return format_html("{}",value)

class CommitmentFilter(FilterSet):
    class Meta:
        model = TblCompanyCommitment
        fields = {
            "company": ["exact"],
            "item": ["exact"],
            "state": ["exact"],
        }
