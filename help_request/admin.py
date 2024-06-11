from django.contrib import admin

from help_request.models import HelpRecord

# Register your models here.

class HelpRecordAdmin(admin.ModelAdmin):
    fields = ['created_at','created_by','issue_app','issue_url','issue_txt','issue_img','issue_solved']
    list_display = ['issue_app','issue_txt','issue_solved','created_at','created_by','updated_at','updated_by']        
    list_filter = ['issue_app']
    view_on_site = False
    readonly_fields = ['created_at','created_by','issue_app','issue_url','issue_txt','issue_img']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if hasattr(obj,'issue_solved') and not obj.issue_solved:
            return True
        
        return False
    
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user

        super().save_model(request, obj, form, change)                

admin.site.register(HelpRecord,HelpRecordAdmin)