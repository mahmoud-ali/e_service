from django.contrib import admin

from .models import Drajat3lawat, MosamaWazifi,Edara3ama,Edarafar3ia,EmployeeBasic,Settings

admin.site.register(MosamaWazifi)
admin.site.register(Edara3ama)
admin.site.register(Edarafar3ia)

class EmployeeBasicAdmin(admin.ModelAdmin):
    fields = ["name", "mosama_wazifi", "edara_3ama","edara_far3ia", "draja_wazifia","alawa_sanawia","tarikh_ta3in","gasima","atfal","moahil"]        
    
    list_display = ["name", "mosama_wazifi", "edara_3ama","edara_far3ia", "draja_wazifia","alawa_sanawia","tarikh_ta3in"]        
    list_filter = ["edara_3ama","draja_wazifia","alawa_sanawia"]
    view_on_site = False

admin.site.register(EmployeeBasic,EmployeeBasicAdmin)

class Drajat3lawatAdmin(admin.ModelAdmin):
    fields = ["draja_wazifia", "alawa_sanawia", "abtdai","galaa_m3isha", "shakhsia","ma3adin","aadoa"]        
    
    list_display = ["draja_wazifia", "alawa_sanawia", "abtdai","galaa_m3isha", "shakhsia","ma3adin","aadoa"]
    list_filter = ["draja_wazifia"]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(Drajat3lawat,Drajat3lawatAdmin)

class SettingsAdmin(admin.ModelAdmin):
    fields = ["code", "value"]        
    
    list_display = ["code", "value"] 
    list_filter = ["code"]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(Settings,SettingsAdmin)
