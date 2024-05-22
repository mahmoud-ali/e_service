from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import ApplicationDepartmentProcessing

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class ApplicationDepartmentProcessingTable(BaseTable):
    menu_name = "doc_workflow:department_processing_show"
    relation_fields = ["department","action_type"]

    class Meta:
        model = ApplicationDepartmentProcessing
        template_name = "django_tables2/bootstrap.html"
        fields = ("department","action_type","app_record__company","app_record__app_type","action_state")
        empty_text = _("No records.")        

    def render_department(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_action_state(self,value,record):
        return format_html("{}",value)

class ApplicationDepartmentProcessingFilter(FilterSet):
    class Meta:
        model = ApplicationDepartmentProcessing
        fields = {
            "department": ["exact"],
            "action_state": ["exact"],
        }
