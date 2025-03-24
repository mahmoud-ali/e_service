from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from production_control.forms import GoldProductionFormForm, GoldShippingFormAlloyForm, GoldShippingFormForm, TblCompanyProductionAutocomplete
from production_control.models import STATE_CONFIRMED, GoldProductionForm, GoldProductionFormAlloy, GoldShippingForm, GoldShippingFormAlloy
from workflow.admin_utils import create_main_form

from django.db import models
from django.forms import TextInput

from django.urls import reverse
from django.utils.html import format_html
from django.urls import path

from .utils import get_company_types

class LogMixin:
    def save_model(self, request, obj, form, change):
        try:
            if not obj.pk:  # New object
                obj.created_by = request.user
                obj.source_state = request.user.hse_tra_state.state

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

        try:
            source_state = request.user.hse_tra_state.state
            qs = qs.filter(source_state=source_state)
        except:
            pass
        return qs

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
        'list_display': ["company","date","form_no","total_weight","state","show_certificate_link"],
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
            if isinstance(inline.model,GoldShippingFormAlloy):
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

move_main_mixins = [LogMixin,GoldShippingMixin]
move_main_class = {
    'model': GoldShippingForm,
    'mixins': [],
    'kwargs': {
        'form': GoldShippingFormForm,
        'list_display': ["company","date","form_no","state","show_certificate_link"],
        'list_filter': ["state","date"],
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
