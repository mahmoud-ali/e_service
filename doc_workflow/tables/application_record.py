from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import ApplicationRecord

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class ApplicationRecordTable(BaseTable):
    menu_name = "doc_workflow:app_record_show"
    relation_fields = ["company"]

    class Meta:
        model = ApplicationRecord
        template_name = "django_tables2/bootstrap.html"
        fields = ("company","app_type","state","created_at","updated_at")
        empty_text = _("No records.")        

    def render_company(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        return format_html("{}",value)

class ApplicationRecordFilter(FilterSet):
    class Meta:
        model = ApplicationRecord
        fields = {
            "company": ["exact"],
            "app_type": ["exact"],
            "state": ["exact"],
        }
