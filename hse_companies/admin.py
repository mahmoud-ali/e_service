from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from workflow.admin_utils import create_main_form

from hse_companies.models import AppHSECorrectiveAction, AppHSEPerformanceReport, AppHSEPerformanceReportActivities, AppHSEPerformanceReportAuditorComment, AppHSEPerformanceReportBillsOfQuantities, AppHSEPerformanceReportCadastralOperations, AppHSEPerformanceReportCadastralOperationsTwo, AppHSEPerformanceReportCatering, AppHSEPerformanceReportChemicalUsed, AppHSEPerformanceReportCyanideCNStorageSpecification, AppHSEPerformanceReportCyanideTable, AppHSEPerformanceReportDiseasesForWorkers, AppHSEPerformanceReportExplosivesUsed, AppHSEPerformanceReportExplosivesUsedSpecification, AppHSEPerformanceReportFireFighting, AppHSEPerformanceReportManPower, AppHSEPerformanceReportOilUsed, AppHSEPerformanceReportOtherChemicalUsed, AppHSEPerformanceReportProactiveIndicators, AppHSEPerformanceReportStatisticalData, AppHSEPerformanceReportTherapeuticUnit, AppHSEPerformanceReportWasteDisposal, AppHSEPerformanceReportWaterUsed, AppHSEPerformanceReportWorkEnvironment

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
    
class AppHSEPerformanceReportMixin:
    @admin.display(description=_('Ask AI'))
    def ask_ai_link(self, obj):
        url = reverse('profile:app_hse_performance_ai',args=[obj.id])
        return format_html('<a target="_blank" class="viewlink" href="{url}">'+_('Ask AI')+'</a>',
                    url=url
                )

report_main_mixins = [AppHSEPerformanceReportMixin,LogMixin]
report_main_class = {
    'model': AppHSEPerformanceReport,
    'mixins': [],
    'kwargs': {
        'list_display': ("company", "year", "month","album","ask_ai_link"),
        'list_filter': ('year', 'month','state'),
        'readonly_fields':('company',),
        'fields': ("company", "year", "month","album",),
        'save_as_continue': False,
        'view_on_site': False,
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
    'AppHSEPerformanceReportFireFighting': {
        'model': AppHSEPerformanceReportFireFighting,
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
    'AppHSEPerformanceReportWorkEnvironment': {
        'model': AppHSEPerformanceReportWorkEnvironment,
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
    'AppHSEPerformanceReportProactiveIndicators': {
        'model': AppHSEPerformanceReportProactiveIndicators,
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
    'AppHSEPerformanceReportActivities': {
        'model': AppHSEPerformanceReportActivities,
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
    'AppHSEPerformanceReportChemicalUsed': {
        'model': AppHSEPerformanceReportChemicalUsed,
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
    'AppHSEPerformanceReportOtherChemicalUsed': {
        'model': AppHSEPerformanceReportOtherChemicalUsed,
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
    'AppHSEPerformanceReportCyanideTable': {
        'model': AppHSEPerformanceReportCyanideTable,
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
    'AppHSEPerformanceReportCyanideCNStorageSpecification': {
        'model': AppHSEPerformanceReportCyanideCNStorageSpecification,
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
    'AppHSEPerformanceReportWaterUsed': {
        'model': AppHSEPerformanceReportWaterUsed,
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
    'AppHSEPerformanceReportOilUsed': {
        'model': AppHSEPerformanceReportOilUsed,
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
    'AppHSEPerformanceReportWasteDisposal': {
        'model': AppHSEPerformanceReportWasteDisposal,
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
    'AppHSEPerformanceReportTherapeuticUnit': {
        'model': AppHSEPerformanceReportTherapeuticUnit,
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
    'AppHSEPerformanceReportDiseasesForWorkers': {
        'model': AppHSEPerformanceReportDiseasesForWorkers,
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
    'AppHSEPerformanceReportStatisticalData': {
        'model': AppHSEPerformanceReportStatisticalData,
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
    'AppHSEPerformanceReportCatering': {
        'model': AppHSEPerformanceReportCatering,
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
    'AppHSEPerformanceReportExplosivesUsed': {
        'model': AppHSEPerformanceReportExplosivesUsed,
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
    'AppHSEPerformanceReportExplosivesUsedSpecification': {
        'model': AppHSEPerformanceReportExplosivesUsedSpecification,
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
    'AppHSEPerformanceReportBillsOfQuantities': {
        'model': AppHSEPerformanceReportBillsOfQuantities,
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
    'AppHSEPerformanceReportCadastralOperations': {
        'model': AppHSEPerformanceReportCadastralOperations,
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
    'AppHSEPerformanceReportCadastralOperationsTwo': {
        'model': AppHSEPerformanceReportCadastralOperationsTwo,
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
    'AppHSEPerformanceReportAuditorComment': {
        'model': AppHSEPerformanceReportAuditorComment,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_cmpny_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
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
    'AppHSECorrectiveAction': {
        'model': AppHSECorrectiveAction,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            # 'min_num': 1,
            'view_on_site': False,
        },
        'groups': {
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
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

report_model_admin, report_inlines = create_main_form(report_main_class,report_inline_classes,report_main_mixins)

admin.site.register(report_model_admin.model,report_model_admin)


##############Corrective actions######################
corrective_main_mixins = [LogMixin]
corrective_main_class = {
    'model': AppHSECorrectiveAction,
    'mixins': [],
    'kwargs': {
        'list_display': ( "report__company","from_dt","to_dt"),
        'list_filter': ("from_dt","to_dt",'state'),
        'fields': ("report", "corrective_action", "from_dt","to_dt",),
        'save_as_continue': False,
        'view_on_site': False,
    },
    'groups': {
        'hse_cmpny_state_mngr':{
            'permissions': {
                AppHSECorrectiveAction.STATE_STATE_MNGR_SUBMIT: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_STATE_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_DEPARTMENT_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_GM_APPROVE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_department_mngr':{
            'permissions': {
                AppHSECorrectiveAction.STATE_STATE_MNGR_SUBMIT: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_STATE_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_DEPARTMENT_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_GM_APPROVE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_gm':{
            'permissions': {
                AppHSECorrectiveAction.STATE_STATE_MNGR_SUBMIT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_STATE_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_DEPARTMENT_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_GM_APPROVE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

corrective_inline_classes = {}

corrective_model_admin, corrective_inlines = create_main_form(corrective_main_class,corrective_inline_classes,corrective_main_mixins)

admin.site.register(corrective_model_admin.model,corrective_model_admin)
