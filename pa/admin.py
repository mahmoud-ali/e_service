from django.contrib import admin

from pa.forms.commitment import TblCompanyCommitmentAdminForm
from pa.forms.payment import TblCompanyPaymentAdminForm
from pa.forms.request import TblCompanyRequestAdminForm
from .models import LkpItem, LkpPaymentMethod,TblCompanyCommitmentMaster,TblCompanyCommitmentDetail, TblCompanyCommitmentSchedular, TblCompanyOpenningBalanceDetail, TblCompanyOpenningBalanceMaster, TblCompanyPaymentDetail, TblCompanyPaymentMaster, TblCompanyPaymentMethod, TblCompanyRequestDetail, TblCompanyRequestMaster, TblCompanyRequestReceive

class LogAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                



admin.site.register(LkpItem)
admin.site.register(LkpPaymentMethod)

class TblCompanyOpenningBalanceMasterDetailInline(admin.TabularInline):
    model = TblCompanyOpenningBalanceDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class TblCompanyOpenningBalanceMasterAdmin(LogAdminMixin,admin.ModelAdmin):
    model = TblCompanyOpenningBalanceMaster
    inlines = [TblCompanyOpenningBalanceMasterDetailInline]     
    
    list_display = ["company","currency","state", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company","currency","state"]
    view_on_site = False
            
admin.site.register(TblCompanyOpenningBalanceMaster, TblCompanyOpenningBalanceMasterAdmin)

class TblCompanyCommitmentMasterDetailInline(admin.TabularInline):
    model = TblCompanyCommitmentDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class TblCompanyCommitmentMasterAdmin(LogAdminMixin,admin.ModelAdmin):
    model = TblCompanyCommitmentAdminForm
    inlines = [TblCompanyCommitmentMasterDetailInline]     
    
    list_display = ["company", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
            
admin.site.register(TblCompanyCommitmentMaster, TblCompanyCommitmentMasterAdmin)

class TblCompanyCommitmentSchedularAdmin(LogAdminMixin,admin.ModelAdmin):
    model = TblCompanyCommitmentSchedular
    
    list_display = ["commitment", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["commitment"]
    view_on_site = False
            
admin.site.register(TblCompanyCommitmentSchedular, TblCompanyCommitmentSchedularAdmin)

class TblCompanyRequestMasterDetailInline(admin.TabularInline):
    model = TblCompanyRequestDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class TblCompanyRequestReceiveInline(admin.TabularInline):
    model = TblCompanyRequestReceive
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class TblCompanyRequestMasterAdmin(LogAdminMixin,admin.ModelAdmin):
    form = TblCompanyRequestAdminForm
    inlines = [TblCompanyRequestMasterDetailInline,TblCompanyRequestReceiveInline]     
    
    list_display = ["commitment","payment_state", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["commitment"]
    view_on_site = False
            
admin.site.register(TblCompanyRequestMaster, TblCompanyRequestMasterAdmin)

class TblCompanyPaymentMasterDetailInline(admin.TabularInline):
    model = TblCompanyPaymentDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class TblCompanyPaymentMethodInline(admin.TabularInline):
    model = TblCompanyPaymentMethod
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class TblCompanyPaymentMasterAdmin(LogAdminMixin,admin.ModelAdmin):
    form = TblCompanyPaymentAdminForm
    inlines = [TblCompanyPaymentMasterDetailInline,TblCompanyPaymentMethodInline]     
    
    list_display = ["request", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["request"]
    view_on_site = False
            
admin.site.register(TblCompanyPaymentMaster, TblCompanyPaymentMasterAdmin)
