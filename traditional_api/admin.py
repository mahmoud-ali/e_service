from django.contrib import admin

from traditional_api.models import LkpSoag, LkpState, TblCollector, TblInvoice

class LoggingAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(LkpState)
admin.site.register(LkpSoag)

class TblCollectorAdmin(LoggingAdminMixin,admin.ModelAdmin):
    field = ['user','name','state','soag']
    
    list_display = ['user','name','state','soag']
    list_filter = ['state','soag']
    view_on_site = False

    class Media:
        js = ('admin/js/jquery.init.js','traditional_api/js/lkp_state_change.js')

admin.site.register(TblCollector, TblCollectorAdmin)

class TblInvoiceAdmin(LoggingAdminMixin,admin.ModelAdmin):
    field = ['collector','mo3adin_name','quantity_in_shoal','amount']
    
    list_display = ['id','collector','mo3adin_name','quantity_in_shoal','amount']
    list_filter = ['collector__state','collector__soag','collector']
    view_on_site = False
            
admin.site.register(TblInvoice, TblInvoiceAdmin)
