from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from .models import AppForignerMovement,AppBorrowMaterial

class AppTable(tables.Table):
    menu_name = None
    relation_fields = []

class AppForignerMovementTable(AppTable):
    menu_name = "profile:app_foreigner_show"
    relation_fields = ["nationality"]

    class Meta:
        model = AppForignerMovement
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","route_from","route_to","period_from","period_to","address_in_sudan","nationality","passport_no")
        empty_text = _("No records.")        

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)
        
class AppBorrowMaterialTable(AppTable):
    menu_name = "profile:app_borrow_show"
    relation_fields = ["company_from"]

    class Meta:
        model = AppBorrowMaterial
        template_name = "django_tables2/bootstrap.html"
        fields = ("id","company_from","borrow_date")        
        empty_text = _("No records.")

    def render_id(self,value):
        return format_html("<a href={}>{}</a>",reverse_lazy(self.menu_name,args=(value,)),value)
        
