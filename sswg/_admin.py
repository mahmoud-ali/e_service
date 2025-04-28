from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.template.response import TemplateResponse
from django.contrib.admin.utils import (
    flatten_fieldsets,
    unquote,
)
from django.contrib.admin import helpers
from django.contrib.admin.options import TO_FIELD_VAR
from sswg.forms import TransferRelocationFormDataForm
from .models import BasicForm, CompanyDetails, MmAceptanceData, TransferRelocationFormData, SSMOData, MOCSData, CBSData, SmrcNoObjectionData

class LogMixin:
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # New inline object
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()

    def has_delete_permission(self, request, obj=None):
        # if obj and obj.state == BasicForm.STATE_1:
        #     return True
        
        return False

report_main_mixins = [LogMixin]
report_main_class = {
    'model': BasicForm,
    'mixins': [],
    'kwargs': {
        'list_display': ('sn_no', 'date'),
        'search_fields': ('sn_no', 'date'),
        'exclude':('state',),
        'save_as_continue': False,
        'view_on_site': False,
    },
    'groups': {
        'sswg_secretary':{
            'permissions': {
                BasicForm.STATE_1: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                BasicForm.STATE_2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                BasicForm.STATE_3: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                BasicForm.STATE_4: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                BasicForm.STATE_5: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                BasicForm.STATE_6: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                BasicForm.STATE_7: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                BasicForm.STATE_8: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                BasicForm.STATE_9: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                BasicForm.STATE_10: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

report_inline_classes = {
    'AppHSEPerformanceReportManPower': {
        'model': AppHSEPerformanceReportManPower,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
        },
        'groups': {
            'hse_cmpny_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
}