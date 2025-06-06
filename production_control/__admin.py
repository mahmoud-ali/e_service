from django.db import models

from django.contrib import admin
from django.forms import TextInput
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

# from rest_framework.authtoken.admin import TokenAdmin

from production_control.forms import GoldProductionFormForm, GoldProductionUserDetailForm, GoldProductionUserForm, GoldShippingFormAlloyForm, GoldShippingFormForm, MoragibForm, TblCompanyProductionAutocomplete
from production_control.models import STATE_CONFIRMED, STATE_DRAFT, GoldProductionForm, GoldProductionFormAlloy, GoldProductionUser, GoldProductionUserDetail, GoldShippingForm, GoldShippingFormAlloy, LkpMoragib

from .utils import get_company_types

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

class AuditorMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve","pro_company_application_show")).exists():
            return qs.filter(company__company_type__in= get_company_types(request))
        
        try:
            company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
            return qs.filter(company__id__in=company_lst)
        except:
            pass

        return qs.none() #super().get_queryset(request)
    
    def has_add_permission(self, request):
        try:
            company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
            return super().has_add_permission(request)
        except Exception as e:
            # print('err',e)
            pass

        return False

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
            if obj and obj.state == STATE_DRAFT:
                return True

            return False

        try:
            company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
            if obj and obj.state != STATE_DRAFT:
                return False

            return super().has_change_permission(request,obj)
        except:
            pass
        
        return False

    def has_delete_permission(self, request, obj=None):
        if obj and obj.state != STATE_DRAFT:
            return False

        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
            if obj and obj.state == STATE_DRAFT:
                return True

        try:
            company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
            if obj and obj.state != STATE_DRAFT:
                return False

            return super().has_delete_permission(request,obj)
        except:
            pass

        return False

# TokenAdmin.raw_id_fields = ['user']

@admin.register(LkpMoragib)
class LkpMoragibAdmin(admin.ModelAdmin):
    model = LkpMoragib
    form = MoragibForm
    list_display = ["name","user","company_type"]
    search_fields = ["name","user__email"]
    list_filter = ["company_type"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve","production_control_auditor_distributor")).exists():
            return qs.filter(company_type__in= get_company_types(request))
        
        return qs.none()

class GoldProductionUserDetailInline(admin.TabularInline):
    model = GoldProductionUserDetail
    form = GoldProductionUserDetailForm
    # fields = ['company']

    extra = 1    

    class Media:
        js = ('admin/js/jquery.init.js',"production_control/js/company_change.js",)


class GoldProductionUserAdmin(StateMixin,LogAdminMixin,admin.ModelAdmin):
    model = GoldProductionUser
    inlines = [GoldProductionUserDetailInline]
    form = GoldProductionUserForm
    list_display = ["moragib_name","companies","company_type","state"] #"user","name",
    list_filter = ["moragib__company_type","state"]
    actions=['end_distribution']
    autocomplete_fields = ["moragib"]

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,GoldProductionUserDetailInline):
                formset.form = GoldProductionUserDetailForm
                formset.form.company_types = get_company_types(request)

            yield formset,inline

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs= qs.prefetch_related(models.Prefetch("goldproductionuserdetail_set"))

        if request.user.is_superuser:
            return qs

        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
            ids = GoldProductionUserDetail.objects.filter(company__company_type__in= get_company_types(request)).values_list("master")
            return qs.filter(id__in=ids)

        # return qs.filter(user__groups__name__in=get_company_types(request))
        
        return qs

    def has_add_permission(self, request):        
        if not request.user.groups.filter(name__in=("production_control_auditor_distributor",)).exists():
            return False
        
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if not obj or obj.state != STATE_DRAFT:
            return False

        if not request.user.groups.filter(name__in=("production_control_auditor_distributor",)).exists():
            return False
                
        return super().has_change_permission(request,obj)

    @admin.action(description=_('end distribution'))
    def end_distribution(self, request, queryset):
        for obj in queryset:
            # obj.state = GoldProductionUser.STATE_EXPIRED
            # obj.save()
            # self.log_change(request,obj,_('state_expired'))

            obj.goldproductionuserdetail_set.all().delete()
            obj.delete()

    @admin.display(description=_('company_type'))
    def company_type(self, obj):
        if obj.moragib and hasattr(obj.moragib,"company_type"):
            return f'{obj.moragib.get_company_type_display()}'
        
        return '-'

    @admin.display(description=_('company'))
    def companies(self, obj):
        return "، ".join(obj.goldproductionuserdetail_set.all().values_list('company__name_ar',flat=True))

    @admin.display(description=_('moragib'))
    def moragib_name(self, obj):
        return obj.moragib.name

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("company_list/", TblCompanyProductionAutocomplete.as_view(),name="lkp_company_list"),
        ]
        return my_urls + urls

admin.site.register(GoldProductionUser, GoldProductionUserAdmin)

class GoldProductionFormAlloyInline(admin.TabularInline):
    model = GoldProductionFormAlloy
    fields = ['alloy_serial_no','alloy_weight','alloy_added_gold']
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    
    extra = 10 

class GoldProductionFormAdmin(AuditorMixin,StateMixin,LogAdminMixin,admin.ModelAdmin):
    model = GoldProductionForm
    inlines = [GoldProductionFormAlloyInline]
    form = GoldProductionFormForm
    list_display = ["company","date","form_no","total_weight","state","show_certificate_link"]
    list_filter = ["state","date"]
    actions=['approved','draft']
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = GoldProductionFormForm

        try:
            if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
                if obj:
                    company_lst = [obj.company.id]
                    kwargs["form"].company_list = company_lst
                else:
                    kwargs["form"].company_types = get_company_types(request)
            else:
                company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
                kwargs["form"].company_list = company_lst

        except:
            pass

        return super().get_form(request, obj, **kwargs)

    @admin.display(description=_('total_weight'))
    def total_weight(self, obj):
        return f'{obj.total_weight():,}'

    @admin.display(description=_('Show certificate'))
    def show_certificate_link(self, obj):
        url = reverse('production:production_certificate')
        return format_html('<a target="_blank" class="viewlink" href="{url}?id={id}">'+_('Show certificate')+'</a>',
                    url=url,id=obj.id
                )

    def get_actions(self, request):
        actions = super().get_actions(request)

        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).count() == 0:
            if "approved" in actions:
                del actions['approved']

            if "draft" in actions:
                del actions['draft']

        return actions

    @admin.action(description=_('approved_action'))
    def approved(self, request, queryset):
        for obj in queryset:
            if obj.state == STATE_CONFIRMED:
                obj.state = GoldProductionForm.STATE_APPROVED
                obj.save()
                self.log_change(request,obj,_('state_confirmed'))

    @admin.action(description=_('draft_action'))
    def draft(self, request, queryset):
        for obj in queryset:
            if obj.state == STATE_CONFIRMED:
                obj.state = STATE_DRAFT
                obj.save()
                self.log_change(request,obj,_('state_draft'))

admin.site.register(GoldProductionForm, GoldProductionFormAdmin)

class GoldShippingFormInline(admin.TabularInline):
    model = GoldShippingFormAlloy
    fields = ['alloy_serial_no'] #,'alloy_weight'
    extra = 10  

class GoldShippingFormAdmin(AuditorMixin,StateMixin,LogAdminMixin,admin.ModelAdmin):
    model = GoldShippingForm
    inlines = [GoldShippingFormInline]
    form = GoldShippingFormForm
    list_display = ["company","date","form_no","state","show_certificate_link"]
    list_filter = ["state","date"]
    actions=['approved','draft']

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = GoldShippingFormForm

        try:
            if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).exists():
                if obj:
                    company_lst = [obj.company.id]
                    kwargs["form"].company_list = company_lst
                else:
                    kwargs["form"].company_types = get_company_types(request)

            else:
                company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('company',flat=True)
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
                    formset.form.company_ids = [obj.company.id]
                else:
                    try:
                        formset.form.company_ids = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.values_list('company')
                    except Exception as e:
                        formset.form.company_ids = []
                        print('err',e)

            yield formset,inline

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)               
        
    def get_actions(self, request):
        actions = super().get_actions(request)

        if request.user.groups.filter(name__in=("pro_company_application_accept","pro_company_application_approve")).count() == 0:
            if "approved" in actions:
                del actions['approved']

            if "draft" in actions:
                del actions['draft']

        return actions

    @admin.display(description=_('Show certificate'))
    def show_certificate_link(self, obj):
        url = reverse('production:shipping_certificate')
        return format_html('<a target="_blank" class="viewlink" href="{url}?id={id}">'+_('Show certificate')+'</a>',
                    url=url,id=obj.id
                )

    @admin.action(description=_('approved_action'))
    def approved(self, request, queryset):
        for obj in queryset:
            obj.state = GoldProductionForm.STATE_APPROVED
            obj.save()
            self.log_change(request,obj,_('state_confirmed'))

    @admin.action(description=_('draft_action'))
    def draft(self, request, queryset):
        for obj in queryset:
            obj.state = STATE_DRAFT
            obj.save()
            self.log_change(request,obj,_('state_draft'))


admin.site.register(GoldShippingForm, GoldShippingFormAdmin)

