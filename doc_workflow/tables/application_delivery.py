from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from ..models import ApplicationDelivery

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class ApplicationDeliveryTable(BaseTable):
    menu_name = "doc_workflow:app_delivery_show"
    relation_fields = []

    class Meta:
        model = ApplicationDelivery
        template_name = "django_tables2/bootstrap.html"
        fields = ("destination","app_record__company","app_record__app_type","delivery_state")
        empty_text = _("No records.")        

    def render_destination(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_delivery_state(self,value,record):
        return format_html("{}",value)

class ApplicationDeliveryFilter(FilterSet):
    class Meta:
        model = ApplicationDelivery
        fields = {
            "destination": ["exact"],
            "delivery_state": ["exact"],
        }
