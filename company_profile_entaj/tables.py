from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables

from company_profile_entaj.models import ForeignerPermission, ForeignerRecord

class AppTable(tables.Table):
    menu_name = None
    relation_fields = []


class AppForeignerRecordTable(AppTable):
    menu_name = "profile:app_foreigner_record_show"
    relation_fields = []

    add_permission = tables.LinkColumn(
        "profile:app_foreigner_permission_record_add",  # name of your URL pattern
        args=[tables.A("id")],  # arguments for the URL (id in this case)
        text="إضافة مستند",        # link text
        verbose_name="العمليات"
    )

    class Meta:
        model = ForeignerRecord
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","name","position","department","employment_type",)                
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)

class AppForeignerPermissionTable(tables.Table):
    class Meta:
        model = ForeignerPermission
        template_name = "django_tables2/bootstrap.html"
        fields = ("permission_type","type_id","validity_due_date","attachment","state",)                
        empty_text = _("No records.")
