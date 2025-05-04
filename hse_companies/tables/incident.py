from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from hse_companies.models.incidents import IncidentInfo

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class IncidentInfoTable(BaseTable):
    menu_name = "hse_companies:incident_show"
    relation_fields = ["company"]

    class Meta:
        model = IncidentInfo
        template_name = "django_tables2/bootstrap.html"
        fields = ("company","incident_category", "incident_type","classification","state")
        empty_text = _("No records.")        

    def render_company(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        return format_html("{}",value)

class IncidentInfoFilter(FilterSet):
    # company = ModelChoiceFilter(queryset=companies, label=_('company'))   
    # state = ChoiceFilter(choices=STATE_TYPE_CHOICES,field_name='state', label=_('record_state'))   
    class Meta:
        model = IncidentInfo
        fields = {
            # "company": ["exact"],
            "state": ["exact"],
        }

    # @property
    # def qs(self):
    #     parent = super().qs

    #     if not self.request or not self.request.user:
    #         return parent.none()

    #     return parent.filter(company_type__in=get_company_types_from_groups(self.request.user))