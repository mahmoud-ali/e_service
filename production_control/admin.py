from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompany
from production_control.forms import GoldProductionFormForm, GoldProductionUserDetailForm, GoldProductionUserForm, GoldShippingFormAlloyForm, GoldShippingFormForm
from production_control.models import STATE_CONFIRMED, STATE_DRAFT, GoldProductionForm, GoldProductionFormAlloy, GoldProductionUser, GoldProductionUserDetail, GoldShippingForm, GoldShippingFormAlloy

def get_company_types(request):
    company_types = []

    if request.user.groups.filter(name="company_type_entaj").exists():
        company_types += [TblCompany.COMPANY_TYPE_ENTAJ]
    if request.user.groups.filter(name="company_type_mokhalfat").exists():
        company_types += [TblCompany.COMPANY_TYPE_MOKHALFAT]
    if request.user.groups.filter(name="company_type_emtiaz").exists():
        company_types += [TblCompany.COMPANY_TYPE_EMTIAZ]
    if request.user.groups.filter(name="company_type_sageer").exists():
        company_types += [TblCompany.COMPANY_TYPE_SAGEER]

    return company_types

class LogAdminMixin:
    view_on_site = False
    
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                
        
class StateMixin:
    save_as_continue = False

    def change_view(self,request,object_id, form_url='', extra_context=None):
        template = super().change_view(request,object_id, form_url, extra_context)
        if request.POST.get('_save_confirm',None):
            obj = self.get_queryset(request).get(id=object_id)
            obj.state = STATE_CONFIRMED
            obj.save()
            self.log_change(request,obj,_('state_confirmed'))

        return template

class GoldProductionUserDetailInline(admin.TabularInline):
    model = GoldProductionUserDetail
    fields = ['company']
    extra = 1    

class GoldProductionUserAdmin(StateMixin,LogAdminMixin,admin.ModelAdmin):
    model = GoldProductionUser
    inlines = [GoldProductionUserDetailInline]
    form = GoldProductionUserForm
    list_display = ["user","name"]

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,GoldProductionUserDetailInline):
                formset.form = GoldProductionUserDetailForm
                formset.form.company_types = get_company_types(request)

            yield formset,inline

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
            ids = GoldProductionUserDetail.objects.filter(company__company_type__in= get_company_types(request)).values_list("master")
            return qs.filter(id__in=ids)
        
        return qs

    def has_add_permission(self, request):        
        if not request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
            return False
        
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if not request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
            return False
        
        if not obj or obj.state == STATE_CONFIRMED:
            return False
        
        return super().has_change_permission(request,obj)

admin.site.register(GoldProductionUser, GoldProductionUserAdmin)

class AuditorMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
            return qs.filter(company__company_type__in= get_company_types(request))
        
        try:
            company_lst = request.user.gold_production_user.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
            return qs.filter(company__id__in=company_lst)
        except:
            pass

        return super().get_queryset(request)
    
    def has_add_permission(self, request):        
        try:
            company_lst = request.user.gold_production_user.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
            return super().has_add_permission(request)
        except Exception as e:
            print('err',e)
            pass

        return False

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
            return True

        try:
            company_lst = request.user.gold_production_user.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
            return super().has_change_permission(request,obj)
        except:
            pass
        
        return False

    def has_delete_permission(self, request, obj=None):
        try:
            company_lst = request.user.gold_production_user.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
            return super().has_delete_permission(request,obj)
        except:
            pass

        return False

class GoldProductionFormAlloyInline(admin.TabularInline):
    model = GoldProductionFormAlloy
    fields = ['alloy_serial_no','alloy_weight','alloy_jaf','alloy_khabath','alloy_added_gold','alloy_remaind']
    extra = 1    

class GoldProductionFormAdmin(AuditorMixin,StateMixin,LogAdminMixin,admin.ModelAdmin):
    model = GoldProductionForm
    inlines = [GoldProductionFormAlloyInline]
    form = GoldProductionFormForm
    list_display = ["company","date","form_no","state"]
    list_filter = ["state","date"]

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = GoldProductionFormForm

        try:
            if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
                kwargs["form"].company_types = get_company_types(request)
            else:
                company_lst = request.user.gold_production_user.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
                kwargs["form"].company_list = company_lst

        except:
            pass

        return super().get_form(request, obj, **kwargs)

admin.site.register(GoldProductionForm, GoldProductionFormAdmin)

class GoldShippingFormInline(admin.TabularInline):
    model = GoldShippingFormAlloy
    fields = ['alloy_serial_no','alloy_weight']
    extra = 1    

class GoldShippingFormAdmin(AuditorMixin,StateMixin,LogAdminMixin,admin.ModelAdmin):
    model = GoldShippingForm
    inlines = [GoldShippingFormInline]
    form = GoldShippingFormForm
    list_display = ["company","date","form_no","state"]
    list_filter = ["state","date"]

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = GoldProductionFormForm

        try:
            if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
                kwargs["form"].company_types = get_company_types(request)
            else:
                company_lst = request.user.gold_production_user.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
                kwargs["form"].company_list = company_lst

        except:
            pass

        return super().get_form(request, obj, **kwargs)

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,GoldShippingFormInline):
                formset.form = GoldShippingFormAlloyForm
                if obj:
                    formset.form.master_id = obj.id

            yield formset,inline

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(GoldShippingForm, GoldShippingFormAdmin)

