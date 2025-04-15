from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from production_control.forms import GoldProductionFormForm, GoldProductionSectorUserForm, GoldProductionStateUserForm, GoldProductionUserDetailForm, GoldProductionUserForm, GoldShippingFormAlloyForm, GoldShippingFormForm, MoragibForm, TblCompanyProductionAutocomplete
from production_control.models import STATE_CONFIRMED, STATE_DRAFT, GoldProductionForm, GoldProductionFormAlloy, GoldProductionSectorUser, GoldProductionStateUser, GoldProductionUser, GoldProductionUserDetail, GoldShippingForm, GoldShippingFormAlloy, LkpMoragib
from workflow.admin_utils import create_main_form

from django.db import models
from django.forms import TextInput

from django.urls import reverse
from django.utils.html import format_html
from django.urls import path

from .utils import get_company_types

class LogMixin:
    view_on_site = False

    def save_model(self, request, obj, form, change):
        try:
            if not obj.pk:  # New object
                obj.created_by = request.user

            obj.updated_by = request.user
            super().save_model(request, obj, form, change)
        except:
            pass

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # New inline object
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.groups.filter(name__in=("production_control_sector_mgr",)).exists():
            try:
                company_type = request.user.gold_production_sector_user.company_type
                sector = request.user.gold_production_sector_user.sector
                return qs.filter(
                    company__company_type__in= [company_type],
                    license__state__sector=sector
                )
            except:
                pass

        if request.user.groups.filter(name__in=("production_control_state_mgr",)).exists():
            try:
                company_type = request.user.gold_production_state_user.company_type
                states = request.user.gold_production_state_user.state
                return qs.filter(
                    company__company_type__in= [company_type],
                    license__state__in=states
                )
            except:
                pass
        
        try:
            license_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('license',flat=True)
            return qs.filter(license__id__in=license_lst)
        except:
            pass

        return qs.none() #super().get_queryset(request)
    
    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = self.form

        try:
            if request.user.groups.filter(name__in=("production_control_state_mgr","production_control_sector_mgr")).exists():
                if obj:
                    license_lst = [obj.license.id]
                    kwargs["form"].license_list = license_lst
                # else:
                #     kwargs["form"].company_types = get_company_types(request)
            else:
                license_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=STATE_CONFIRMED).values_list('license',flat=True)
                kwargs["form"].license_list = license_lst

        except:
            pass

        return super().get_form(request, obj, **kwargs)

class GoldProductionMixin:
    class Media:
        js = ('admin/js/jquery.init.js',"production_control/js/company_change_master.js",)

    @admin.display(description=_('Show certificate'))
    def show_certificate_link(self, obj):
        url = reverse('production:production_certificate')
        return format_html('<a target="_blank" class="viewlink" href="{url}?id={id}">'+_('Show certificate')+'</a>',
                    url=url,id=obj.id
                )

    @admin.display(description=_('total_weight'))
    def total_weight(self, obj):
        return f'{obj.total_weight():,}'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("company_list/", TblCompanyProductionAutocomplete.as_view(),name="lkp_company_list"),
        ]
        return my_urls + urls

production_main_mixins = [LogMixin,GoldProductionMixin]
production_main_class = {
    'model': GoldProductionForm,
    'mixins': [],
    'kwargs': {
        'form': GoldProductionFormForm,
        'list_display': ["license","date","form_no","total_weight","state","show_certificate_link"],
        'list_filter': ["state","date"],
        'formfield_overrides': {
            models.FloatField: {"widget": TextInput},
        },
        'save_as_continue': False,
    },
    'groups': {
        'production_control_auditor':{
            'permissions': {
                GoldProductionForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                GoldProductionForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # GoldProductionForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # GoldProductionForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # GoldProductionForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'production_control_state_mgr':{
            'permissions': {
                # GoldProductionForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # GoldProductionForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                GoldProductionForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # GoldProductionForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # GoldProductionForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'production_control_sector_mgr':{
            'permissions': {
                # GoldProductionForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # GoldProductionForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # GoldProductionForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                GoldProductionForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                GoldProductionForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

    },
}

production_inline_classes = {
    'GoldProductionFormAlloy': {
        'model': GoldProductionFormAlloy,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    GoldProductionForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    GoldProductionForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    # GoldProductionForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    # GoldProductionForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    # GoldProductionForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'production_control_state_mgr':{
                'permissions': {
                    # GoldProductionForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    # GoldProductionForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    GoldProductionForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    # GoldProductionForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    # GoldProductionForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'production_control_sector_mgr':{
                'permissions': {
                    # GoldProductionForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    # GoldProductionForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    # GoldProductionForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    GoldProductionForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    GoldProductionForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },

}

production_model_admin, inlines = create_main_form(production_main_class,production_inline_classes,production_main_mixins)

admin.site.register(production_model_admin.model,production_model_admin)


#######################################
class GoldShippingMixin:
    class Media:
        js = ('admin/js/jquery.init.js',"production_control/js/company_change_master.js",)
        
    @admin.display(description=_('Show certificate'))
    def show_certificate_link(self, obj):
        url = reverse('production:shipping_certificate')
        return format_html('<a target="_blank" class="viewlink" href="{url}?id={id}">'+_('Show certificate')+'</a>',
                    url=url,id=obj.id
                )

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if inline.model ==GoldShippingFormAlloy:
                formset.form = GoldShippingFormAlloyForm
                if obj:
                    formset.form.master_id = obj.id
                    formset.form.license_ids = [obj.license.id]
                else:
                    try:
                        formset.form.license_ids = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=GoldShippingForm.STATE_CONFIRMED1).values_list('license')
                    except Exception as e:
                        formset.form.license_ids = []

            yield formset,inline

move_main_mixins = [LogMixin,GoldShippingMixin]
move_main_class = {
    'model': GoldShippingForm,
    'mixins': [],
    'kwargs': {
        'form': GoldShippingFormForm,
        'list_display': ["license","date","form_no","state","show_certificate_link"],
        'list_filter': ["state","date"],
        # 'readonly_fields': ["company"],
        'save_as_continue': False,
    },
    'groups': {
        'production_control_auditor':{
            'permissions': {
                GoldShippingForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                GoldShippingForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # GoldShippingForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # GoldShippingForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # GoldShippingForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'production_control_state_mgr':{
            'permissions': {
                # GoldShippingForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # GoldShippingForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                GoldShippingForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # GoldShippingForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # GoldShippingForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'production_control_sector_mgr':{
            'permissions': {
                # GoldShippingForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # GoldShippingForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # GoldShippingForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                GoldShippingForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                GoldShippingForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

    },
}

move_inline_classes = {
    'GoldShippingFormAlloy': {
        'model': GoldShippingFormAlloy,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    GoldShippingForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    GoldShippingForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    # GoldShippingForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    # GoldShippingForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    # GoldShippingForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'production_control_state_mgr':{
                'permissions': {
                    # GoldShippingForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    # GoldShippingForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    GoldShippingForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    # GoldShippingForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    # GoldShippingForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'production_control_sector_mgr':{
                'permissions': {
                    # GoldShippingForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    # GoldShippingForm.STATE_REVIEW_REQUIRED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    # GoldShippingForm.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    GoldShippingForm.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    GoldShippingForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },

}

move_model_admin, inlines = create_main_form(move_main_class,move_inline_classes,move_main_mixins)

admin.site.register(move_model_admin.model,move_model_admin)

#############################
@admin.register(LkpMoragib)
class LkpMoragibAdmin(admin.ModelAdmin):
    model = LkpMoragib
    form = MoragibForm
    list_display = ["name","user","company_type"]
    search_fields = ["name","user__email"]
    list_filter = ["company_type"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.groups.filter(name__in=("production_control_auditor_distributor",)).exists():
            return qs.filter(company_type__in= get_company_types(request))
        
        return qs.none()

class GoldProductionUserDetailInline(admin.TabularInline):
    model = GoldProductionUserDetail
    form = GoldProductionUserDetailForm
    # fields = ['company']

    extra = 1    

    class Media:
        js = ('admin/js/jquery.init.js',"production_control/js/company_change_detail.js",)


class GoldProductionUserAdmin(admin.ModelAdmin):
    model = GoldProductionUser
    inlines = [GoldProductionUserDetailInline]
    form = GoldProductionUserForm
    list_display = ["moragib_name","companies","company_type","state"] #"user","name",
    list_filter = ["moragib__company_type","state"]
    actions=['approved','end_distribution']
    autocomplete_fields = ["moragib"]

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                
        
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

    @admin.action(description=_('تأكيد الطلبات المحددة'))
    def approved(self, request, queryset):
        for obj in queryset:
            if obj.state == STATE_DRAFT:
                obj.state = STATE_CONFIRMED
                obj.save()
                self.log_change(request,obj,_('state_confirmed'))

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

@admin.register(GoldProductionStateUser)
class GoldProductionStateUserAdmin(admin.ModelAdmin):
    model = GoldProductionStateUser
    form = GoldProductionStateUserForm
    list_display = ["company_type","name","states"]
    list_filter = ["company_type","state"]
    
    def save_model(self, request, obj, form, change):
        try:
            if not obj.pk:  # New object
                obj.created_by = request.user

            obj.updated_by = request.user
            super().save_model(request, obj, form, change)
        except:
            pass

    @admin.display(description=_('states'))
    def states(self, obj):
        return "، ".join(obj.state.values_list('name',flat=True))
        
@admin.register(GoldProductionSectorUser)
class GoldProductionSectorUserAdmin(admin.ModelAdmin):
    model = GoldProductionSectorUser
    form = GoldProductionSectorUserForm
    list_display = ["company_type","name","sector"]
    list_filter = ["company_type","sector"]

    def save_model(self, request, obj, form, change):
        try:
            if not obj.pk:  # New object
                obj.created_by = request.user

            obj.updated_by = request.user
            super().save_model(request, obj, form, change)
        except:
            pass
