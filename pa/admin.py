from django.contrib import admin

from pa.forms.commitment import TblCompanyCommitmentAdminForm, TblCompanyCommitmentDetailForm
from pa.forms.payment import TblCompanyPaymentAdminForm, TblCompanyPaymentDetailForm
from pa.forms.request import TblCompanyRequestAdminForm, TblCompanyRequestDetailsForm
from pa.utils import get_company_types_from_groups
from .models import STATE_TYPE_CONFIRM, LkpItem, LkpPaymentMethod,TblCompanyCommitmentMaster,TblCompanyCommitmentDetail, TblCompanyCommitmentSchedular, TblCompanyOpenningBalanceDetail, TblCompanyOpenningBalanceMaster, TblCompanyPaymentDetail, TblCompanyPaymentMaster, TblCompanyPaymentMethod, TblCompanyRequestDetail, TblCompanyRequestMaster, TblCompanyRequestReceive

class LogAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                



# admin.site.register(LkpItem)
admin.site.register(LkpPaymentMethod)

class LkpItemAdmin(admin.ModelAdmin):
    model = LkpItem
    
    list_display = ["name","company_type","calculation_method"]        
    list_filter = ["company_type","calculation_method"]
    view_on_site = False
            
admin.site.register(LkpItem, LkpItemAdmin)

# class TblCompanyOpenningBalanceMasterDetailInline(admin.TabularInline):
#     model = TblCompanyOpenningBalanceDetail
#     exclude = ["created_at","created_by","updated_at","updated_by"]
#     extra = 1    

# class TblCompanyOpenningBalanceMasterAdmin(LogAdminMixin,admin.ModelAdmin):
#     model = TblCompanyOpenningBalanceMaster
#     inlines = [TblCompanyOpenningBalanceMasterDetailInline]     
    
#     list_display = ["company","currency","state", "created_at", "created_by","updated_at", "updated_by"]        
#     list_filter = ["company","currency","state"]
#     view_on_site = False
            
# admin.site.register(TblCompanyOpenningBalanceMaster, TblCompanyOpenningBalanceMasterAdmin)

class TblCompanyCommitmentMasterDetailInline(admin.TabularInline):
    model = TblCompanyCommitmentDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

    # def get_form(self, request, obj=None, **kwargs):
    #     print("type",obj.commitment.company.company_type)
    #     kwargs["form"] = TblCompanyCommitmentDetailForm
    #     kwargs["form"].company_type = obj.company.company_type
    #     return super().get_form(request, obj, **kwargs)

class TblCompanyCommitmentMasterAdmin(LogAdminMixin,admin.ModelAdmin):
    model = TblCompanyCommitmentAdminForm
    inlines = [TblCompanyCommitmentMasterDetailInline]     
    
    list_display = ["license", "company", "currency","state"]        
    list_filter = ["company__company_type","currency","state"]
    search_fields = ["company__name_ar","company__name_en","license__license_no","license__sheet_no"]
    autocomplete_fields = ["company"]

    view_on_site = False
            
    class Media:
        js = ('admin/js/jquery.init.js','pa/js/lkp_company_change.js')

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,TblCompanyCommitmentMasterDetailInline):
                formset.form = TblCompanyCommitmentDetailForm
                formset.form.company_type = obj.company.company_type
            yield formset,inline

admin.site.register(TblCompanyCommitmentMaster, TblCompanyCommitmentMasterAdmin)

class TblCompanyCommitmentSchedularAdmin(LogAdminMixin,admin.ModelAdmin):
    model = TblCompanyCommitmentSchedular
    
    list_display = ["commitment", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["commitment__company__company_type"]
    autocomplete_fields = ["commitment"]
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
    
    list_display = ["commitment","payment_state", "from_dt", "to_dt","state"]        
    list_filter = ["commitment__company__company_type","currency",'payment_state',"state"]
    search_fields = ["commitment__company__name_ar","commitment__company__name_en","commitment__license__license_no","commitment__license__sheet_no"]
    # autocomplete_fields = ["commitment"]

    view_on_site = False
            
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,TblCompanyRequestMasterDetailInline):
                formset.form = TblCompanyRequestDetailsForm
                formset.form.company_type = get_company_types_from_groups(request.user)[0] #obj.commitment.company.company_type
            yield formset,inline

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "commitment":
            kwargs["queryset"] = TblCompanyCommitmentMaster.objects.filter(state=STATE_TYPE_CONFIRM)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
    
    list_display = ["request", "payment_dt", "currency","exchange_rate", "state"]        
    list_filter = ["request__commitment__company__company_type","currency","state"]
    search_fields = ["request__commitment__company__name_ar","request__commitment__company__name_en"]
    # autocomplete_fields = ["request"]
    view_on_site = False
            
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,TblCompanyPaymentMasterDetailInline):
                formset.form = TblCompanyPaymentDetailForm
                formset.form.company_type = get_company_types_from_groups(request.user)[0] #obj.request.commitment.company.company_type
            yield formset,inline

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        print(db_field.name)
        if db_field.name == "request":
            kwargs["queryset"] = TblCompanyRequestMaster.objects.filter(state=STATE_TYPE_CONFIRM)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(TblCompanyPaymentMaster, TblCompanyPaymentMasterAdmin)
