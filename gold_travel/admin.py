from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from gold_travel.models import AppMoveGold, AppMoveGoldDetails

class LogAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class AppMoveGoldDetailInline(admin.TabularInline):
    model = AppMoveGoldDetails
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppMoveGoldAdmin(LogAdminMixin,admin.ModelAdmin):
    model = AppMoveGold
    inlines = [AppMoveGoldDetailInline]     

    fieldsets = [
        (
            None,
            {
                'fields': ["date","destination"]
            },
        ),
        (
            _("owner data"),
            {
                'fields': ["owner_name","owner_address"]
            },
        ),
        (
            _("representative data"),
            {
                'fields': [("repr_name","repr_phone"),"repr_address",("repr_identity","repr_identity_issue_date")]
            },
        ),
        (
            _("gold data"),
            {
                'fields': [("gold_weight_in_gram","gold_alloy_count"),"gold_description"]
            },
        ),
        (
            _("attachments"),
            {
                'fields': ["attachement_file"]
            },
        ),
    ]
    list_display = ["date","owner_name","repr_name","gold_weight_in_gram","gold_alloy_count"]        
    list_filter = ["owner_name"]
    search_fields = ["owner_name","owner_address","repr_name","repr_phone","repr_identity"]
    view_on_site = False
            
admin.site.register(AppMoveGold, AppMoveGoldAdmin)
