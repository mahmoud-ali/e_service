from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import ApplicationExectiveProcessing

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class ApplicationExectiveProcessingTable(BaseTable):
    menu_name = "doc_workflow:executive_processing_show"
    relation_fields = ["department","action_type"]

    class Meta:
        model = ApplicationExectiveProcessing
        template_name = "django_tables2/bootstrap.html"
        fields = ("department","app_record__company","app_record__app_type","action_type","action_state")
        empty_text = _("No records.")        

    def render_department(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_action_state(self,value,record):
        return format_html("{}",value)

class ApplicationExectiveProcessingFilter(FilterSet):
    class Meta:
        model = ApplicationExectiveProcessing
        fields = {
            "department": ["exact"],
            "action_state": ["exact"],
        }
