from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from ..models import TblCompanyCommitment

class BaseTable(tables.Table):
    menu_name = None
    relation_fields = []

class TblCompanyCommitmentTable(BaseTable):
    menu_name = "profile:app_foreigner_show"
    relation_fields = ["nationality"]

    class Meta:
        model = TblCompanyCommitment
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","route_from","route_to","period_from","period_to","address_in_sudan","nationality","passport_no")
        empty_text = _("No records.")        

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)
