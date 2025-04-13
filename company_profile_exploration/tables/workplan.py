from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet

from company_profile_exploration.models.work_plan import AppWorkPlan

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class AppWorkPlanTable(BaseTable):
    menu_name = "exploration:workplan_show"
    relation_fields = ["company"]

    class Meta:
        model = AppWorkPlan
        template_name = "django_tables2/bootstrap.html"
        fields = ("company","currency","state")
        empty_text = _("No records.")        

    def render_company(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        return format_html("{}",value)

class AppWorkPlanFilter(FilterSet):
    # company = ModelChoiceFilter(queryset=companies, label=_('company'))   
    # state = ChoiceFilter(choices=STATE_TYPE_CHOICES,field_name='state', label=_('record_state'))   
    class Meta:
        model = AppWorkPlan
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