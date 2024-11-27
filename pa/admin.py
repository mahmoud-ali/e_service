from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pa.forms.commitment import TblCompanyCommitmentAdminForm, TblCompanyCommitmentDetailForm
from pa.forms.payment import TblCompanyPaymentAdminForm, TblCompanyPaymentDetailForm
from pa.forms.request import TblCompanyRequestAdminForm, TblCompanyRequestDetailsForm
from pa.utils import get_company_types_from_groups
from .models import STATE_TYPE_CONFIRM, STATE_TYPE_DRAFT, LkpItem, LkpPaymentMethod,TblCompanyCommitmentMaster,TblCompanyCommitmentDetail, TblCompanyCommitmentSchedular, TblCompanyOpenningBalanceDetail, TblCompanyOpenningBalanceMaster, TblCompanyPaymentDetail, TblCompanyPaymentMaster, TblCompanyPaymentMethod, TblCompanyRequestDetail, TblCompanyRequestMaster, TblCompanyRequestReceive

class LogAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class StateMixin:
    save_as_continue = False
        
    def has_add_permission(self, request):        
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if not obj or obj.state==STATE_TYPE_DRAFT:
            return super().has_change_permission(request,obj)
        
        return False

    def has_delete_permission(self, request, obj=None):
        if not obj or obj.state==STATE_TYPE_DRAFT:
            return super().has_delete_permission(request,obj)
        
        return False

    def change_view(self,request,object_id, form_url='', extra_context=None):
        template = super().change_view(request,object_id, form_url, extra_context)
        if request.POST.get('_save_confirm',None):
            obj = self.get_queryset(request).get(id=object_id)
            obj.state = STATE_TYPE_CONFIRM
            obj.save()

        return template

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

class TblCompanyCommitmentMasterAdmin(LogAdminMixin,StateMixin,admin.ModelAdmin):
    model = TblCompanyCommitmentAdminForm
    fields = ['company','license','currency','note']
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
                if obj:
                    formset.form.company_type = obj.company.company_type
                else:
                    formset.form.company_type = get_company_types_from_groups(request.user)[0]
            yield formset,inline

admin.site.register(TblCompanyCommitmentMaster, TblCompanyCommitmentMasterAdmin)

class TblCompanyCommitmentSchedularAdmin(LogAdminMixin,StateMixin,admin.ModelAdmin):
    model = TblCompanyCommitmentSchedular
    readonly_fields = ['state']
    
    list_display = ["commitment","state", "created_at", "created_by","updated_at", "updated_by"]        
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

class TblCompanyRequestMasterAdmin(LogAdminMixin,StateMixin,admin.ModelAdmin):
    form = TblCompanyRequestAdminForm
    inlines = [TblCompanyRequestMasterDetailInline,TblCompanyRequestReceiveInline]     
    
    list_display = ["commitment","payment_state", "from_dt", "to_dt","state","total","sum_of_confirmed_payment"]        
    list_filter = ["commitment__company__company_type","currency",'payment_state',"state"]
    search_fields = ["commitment__company__name_ar","commitment__company__name_en","commitment__license__license_no","commitment__license__sheet_no"]
    list_select_related = ["commitment__license","commitment__company"]
    # autocomplete_fields = ["commitment"]

    view_on_site = False
            
    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = self.form
        if obj and obj.commitment:
            kwargs["form"].commitment_id = obj.commitment.id

        return super().get_form(request, obj, **kwargs)

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,TblCompanyRequestMasterDetailInline):
                formset.form = TblCompanyRequestDetailsForm
                if obj:
                    formset.form.company_type = obj.commitment.company.company_type #get_company_types_from_groups(request.user)[0] #obj.commitment.company.company_type
                else:
                    formset.form.company_type = get_company_types_from_groups(request.user)[0]
            yield formset,inline

    @admin.display(description=_("request_total"))
    def total(self,obj):
        return f'{round(obj.total,2):,}'

    @admin.display(description=_("payments total"))
    def sum_of_confirmed_payment(self,obj):
        return f'{round(obj.sum_of_confirmed_payment,2):,}'

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "commitment":
    #         kwargs["queryset"] = TblCompanyCommitmentMaster.objects.filter(state=STATE_TYPE_CONFIRM)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(TblCompanyRequestMaster, TblCompanyRequestMasterAdmin)

class TblCompanyPaymentMasterDetailInline(admin.TabularInline):
    model = TblCompanyPaymentDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class TblCompanyPaymentMethodInline(admin.TabularInline):
    model = TblCompanyPaymentMethod
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class TblCompanyPaymentMasterAdmin(LogAdminMixin,StateMixin,admin.ModelAdmin):
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
                if obj:
                    formset.form.company_type = obj.request.commitment.company.company_type
                else:
                    formset.form.company_type = get_company_types_from_groups(request.user)[0]
            yield formset,inline

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # print(db_field.name)
        if db_field.name == "request":
            kwargs["queryset"] = TblCompanyRequestMaster.objects.filter(state=STATE_TYPE_CONFIRM)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(TblCompanyPaymentMaster, TblCompanyPaymentMasterAdmin)
