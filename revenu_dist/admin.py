from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib import admin,messages
from django.forms.widgets import TextInput

from revenu_dist.models import LkpPartner, LkpRevenu, LkpRevenuType, LkpRevenuTypeDetail, TblRevenu, TblRevenuDist

class LoggingAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(LkpPartner)

class LkpRevenuTypeDetailInline(admin.TabularInline):
    model = LkpRevenuTypeDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 0

class LkpRevenuTypeAdmin(LoggingAdminMixin,admin.ModelAdmin):
    field = ['name']
    inlines = [LkpRevenuTypeDetailInline]     
    
    list_display = ["name"]        
    view_on_site = False
            
admin.site.register(LkpRevenuType, LkpRevenuTypeAdmin)

class LkpRevenuAdmin(LoggingAdminMixin,admin.ModelAdmin):
    field = ['name','revenu_type']
    
    list_display = ["name"]        
    list_filter = ['revenu_type']
    view_on_site = False
            
admin.site.register(LkpRevenu, LkpRevenuAdmin)

class TblRevenuDetailInline(admin.TabularInline):
    model = TblRevenuDist
    fields = ['partner','amount']
    extra = 0
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class TblRevenuAdmin(LoggingAdminMixin,admin.ModelAdmin):
    fields = [('date','revenu'),('amount','currency'),'name','source']
    
    list_display = ['revenu','distributed_correctly','date','amount','currency','name','source']       
    list_filter =  ['revenu','date','currency','source']       
    view_on_site = False

    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    @admin.display(description=_("Distributed correctly"),boolean=True)
    def distributed_correctly(self, obj):
        return obj.checkDetailsTotalEqualAmount()

    def get_inlines(self,request, obj):
        if obj:
            return [TblRevenuDetailInline]    
        return []

    def save_model(self,request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user

        super().save_formset(request, obj, form, change)
        if not change:       
            obj.distributeAmount()

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        obj = form.save(commit=False)
        if not change:       
            obj.distributeAmount()
        elif not obj.checkDetailsTotalEqualAmount():
            messages.add_message(request,messages.ERROR,_("Double check distribution balance!"))


admin.site.register(TblRevenu, TblRevenuAdmin)
