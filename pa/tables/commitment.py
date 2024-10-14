from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_filters import FilterSet,ModelChoiceFilter,ChoiceFilter

from company_profile.models import TblCompanyProduction
from pa.utils import get_company_types_from_groups


from ..models import TblCompanyCommitmentMaster,STATE_TYPE_CHOICES,STATE_TYPE_DRAFT,STATE_TYPE_CONFIRM

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyCommitmentTable(BaseTable):
    menu_name = "pa:commitment_show"
    relation_fields = ["company"]

    class Meta:
        model = TblCompanyCommitmentMaster
        template_name = "django_tables2/bootstrap.html"
        fields = ("company","currency","state")
        empty_text = _("No records.")        

    def render_company(self,value,record):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(record.id,)),value)

    def render_state(self,value,record):
        return format_html("{}",value)

# def companies(request):
#     query = TblCompanyProduction.objects.all()
#     if request is None:
#         return query.none()

#     query = query.filter(company_type__in=get_company_types_from_groups(request.user))
#     return query

class CommitmentFilter(FilterSet):
    # company = ModelChoiceFilter(queryset=companies, label=_('company'))   
    # state = ChoiceFilter(choices=STATE_TYPE_CHOICES,field_name='state', label=_('record_state'))   
    class Meta:
        model = TblCompanyCommitmentMaster
        fields = {
            "company": ["exact"],
            "state": ["exact"],
        }

    # @property
    # def qs(self):
    #     parent = super().qs

    #     if not self.request or not self.request.user:
    #         return parent.none()

    #     return parent.filter(company_type__in=get_company_types_from_groups(self.request.user))