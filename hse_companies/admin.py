from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompanyProductionLicense
from hse_companies.forms import TblStateRepresentativeForm
from hse_companies.models.incidents import ContributingFactor, FactorsAssessment, IncidentAnalysis, IncidentCost, IncidentInfo, IncidentInjuredPerson,IncidentInjuredPPE,IncidentInjuredDetails, IncidentPhoto, IncidentProperty, IncidentWitness, LeasonLearnt
from workflow.admin_utils import create_main_form

from hse_companies.models import AppHSECorrectiveAction, AppHSECorrectiveActionFeedback, AppHSEPerformanceReport, AppHSEPerformanceReportActivities, AppHSEPerformanceReportAuditorComment, AppHSEPerformanceReportBillsOfQuantities, AppHSEPerformanceReportCadastralOperations, AppHSEPerformanceReportCadastralOperationsTwo, AppHSEPerformanceReportCatering, AppHSEPerformanceReportChemicalUsed, AppHSEPerformanceReportCyanideCNStorageSpecification, AppHSEPerformanceReportCyanideTable, AppHSEPerformanceReportDiseasesForWorkers, AppHSEPerformanceReportExplosivesUsed, AppHSEPerformanceReportExplosivesUsedSpecification, AppHSEPerformanceReportFireFighting, AppHSEPerformanceReportManPower, AppHSEPerformanceReportOilUsed, AppHSEPerformanceReportOtherChemicalUsed, AppHSEPerformanceReportProactiveIndicators, AppHSEPerformanceReportStatisticalData, AppHSEPerformanceReportTherapeuticUnit, AppHSEPerformanceReportWasteDisposal, AppHSEPerformanceReportWaterUsed, AppHSEPerformanceReportWorkEnvironment, TblStateRepresentative

from production_control.models import STATE_CONFIRMED as PRODUCTION_STATE_CONFIRMED
class LogMixin:
    def save_model(self, request, obj, form, change):
        try:
            if not obj.pk:  # New object
                obj.created_by = request.user
                obj.source_state = request.user.hse_cmpny_state.state

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

        if request.user.groups.filter(name__in=("hse_cmpny_department_mngr","hse_cmpny_gm")).exists():
            return qs
        
        if request.user.groups.filter(name__in=("hse_cmpny_state_mngr",)).exists():
            try:
                # company_type = request.user.gold_production_state_user.company_type
                original_state = request.user.hse_cmpny_state.state
                companies = TblCompanyProductionLicense.objects.filter(state=original_state).values_list('company',flat=True)
                   
                return qs.filter(
                    # license__company__company_type__in= [company_type],
                    company__in=companies
                )
            except Exception as e:
                print(e)

        if request.user.groups.filter(name__in=("production_control_auditor",)).exists():
            try:
                company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=PRODUCTION_STATE_CONFIRMED).values_list('company',flat=True)
                return qs.filter(company__id__in=company_lst)
            except Exception as e:
                print(request.user,e)

        return qs.none() #super().get_queryset(request)

class TblStateRepresentativeAdmin(admin.ModelAdmin):
    model = TblStateRepresentative
    form = TblStateRepresentativeForm
    list_display = ["state", "name", "user"]
    list_filter = ["state"]
    
admin.site.register(TblStateRepresentative,TblStateRepresentativeAdmin)

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
        'list_display': ("company","license", "year", "month","state","ask_ai_link"), #,"ask_ai_link"
        'list_filter': ('year', 'month','state'),
        'readonly_fields':('company','license'),
        'fields': ("company","license", "year", "month","album",),
        'save_as_continue': False,
        'view_on_site': False,
    },
    'groups': {
        'production_control_auditor':{
            'permissions': {
                AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_state_mngr':{
            'permissions': {
                AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'production_control_auditor':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            'exclude': ('incident', 'state',),
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
class AppHSECorrectiveActionMixin:
    @admin.display(description=_('الإجراء التصحيحي'))
    def corrective_action_summary(self, obj):
        return obj.corrective_action[:50]

    @admin.display(description=_('تقرير / حادث / مأمورية'))
    def belong_to(self, obj):
        if obj.report:
            return obj.report
        
        if obj.incident:
            return obj.incident
        
        return ""
    
corrective_main_mixins = [AppHSECorrectiveActionMixin,LogMixin]
corrective_main_class = {
    'model': AppHSECorrectiveAction,
    'mixins': [],
    'kwargs': {
        'list_display': ( "belong_to","from_dt","to_dt","corrective_action_summary","state"),
        'list_filter': ("from_dt","to_dt",'state'),
        'fields': ("report", "incident","corrective_action", "from_dt","to_dt",),
        'readonly_fields':('report',),
        'save_as_continue': False,
        'view_on_site': False,
    },
    'groups': {
        'production_control_auditor':{
            'permissions': {
                AppHSECorrectiveAction.STATE_GM_APPROVE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
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
                # AppHSECorrectiveAction.STATE_STATE_MNGR_SUBMIT: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_STATE_MNGR_CONFIRM: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_DEPARTMENT_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_GM_APPROVE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_gm':{
            'permissions': {
                # AppHSECorrectiveAction.STATE_STATE_MNGR_SUBMIT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # AppHSECorrectiveAction.STATE_STATE_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_DEPARTMENT_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_GM_APPROVE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

corrective_inline_classes = {}

corrective_model_admin, corrective_inlines = create_main_form(corrective_main_class,corrective_inline_classes,corrective_main_mixins)

admin.site.register(corrective_model_admin.model,corrective_model_admin)

##########################Corrective actions feedback############
class AppHSECorrectiveActionFeedbackMixin:
    pass

corrective_action_feedback_main_mixins = [LogMixin]
corrective_action_feedback_main_class = {
    'model': AppHSECorrectiveActionFeedback,
    'mixins': [],
    'kwargs': {
        'list_display': ("corrective_action", "percentage", "company_comment","auditor_comment",),
        'list_filter': ('percentage', 'company_comment','state'),
        # 'readonly_fields':('corrective_action',),
        'fields': ("corrective_action", "percentage", "company_comment","auditor_comment",),
        'save_as_continue': False,
        'view_on_site': False,
    },
    'groups': {
        'production_control_auditor':{
            'permissions': {
                AppHSECorrectiveActionFeedback.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                AppHSECorrectiveActionFeedback.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveActionFeedback.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_state_mngr':{
            'permissions': {
                AppHSECorrectiveActionFeedback.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveActionFeedback.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        # 'hse_cmpny_department_mngr':{
        #     'permissions': {
        #         AppHSECorrectiveActionFeedback.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
        #     },
        # },
        # 'hse_cmpny_gm':{
        #     'permissions': {
        #         AppHSECorrectiveActionFeedback.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
        #     },
        # },
    },
}

corrective_action_feedback_inline_classes = {
}

corrective_action_feedback_model_admin, corrective_action_feedback_inlines = create_main_form(corrective_action_feedback_main_class,corrective_action_feedback_inline_classes,corrective_action_feedback_main_mixins)

admin.site.register(corrective_action_feedback_model_admin.model,corrective_action_feedback_model_admin)



###############Incidents#####################
incident_main_mixins = [LogMixin]
incident_main_class = {
    'model': IncidentInfo,
    'mixins': [],
    'kwargs': {
        'list_display': ("company", "incident_category", "incident_type","classification",),
        'list_filter': ('incident_category','incident_type', 'classification','state'),
        # 'readonly_fields':('company',),
        # 'fields': ("company", "year", "month","album",),
        'fieldsets': [
            (None,{"fields": ("company", ("incident_category","classification"), ("incident_type","other_type_details"))}),
            ("تفاصيل الحادث Details of Incident",{"fields": (("equipment_vehicle_no","client_contractor"), "date_time_occurred","date_time_reported","reported_to","location","incident_description")}),
            ("تفاصيل العملية والمكان في زمن الحادث Location and Operation at Time of Incident",{"fields": ("precise_location", "precise_operation","site_closed_now","site_closed_because_of_incident")}),
        ],
        'save_as_continue': False,
        'view_on_site': False,
    },
    'groups': {
        'production_control_auditor':{
            'permissions': {
                IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_state_mngr':{
            'permissions': {
                IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_department_mngr':{
            'permissions': {
                IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_gm':{
            'permissions': {
                IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'general_manager':{
            'permissions': {
                IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

incident_inline_classes = {
    'IncidentInjuredPerson': {
        'model': IncidentInjuredPerson,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'min_num': 1,
            'extra': 0,
            'fieldsets': [
                (None,{"fields": ("injured_surname", ("injured_position","injured_experience_years","injured_date_of_birth"),"injured_employment_basis",("lost_time_injury","lost_days"))}),
            ],

        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'IncidentInjuredPPE': {
        'model': IncidentInjuredPPE,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'min_num': 1,
            'extra': 0,
            'fieldsets': [
                (None,{"fields": (("ppe_gloves", "ppe_helmet","ppe_safety_cloth","ppe_safety_shoes"), ("ppe_face_protection", "ppe_ear_protection","ppe_mask","ppe_other"))}),
            ],

        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'IncidentInjuredDetails': {
        'model': IncidentInjuredDetails,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'min_num': 1,
            'extra': 0,
            'fieldsets': [
                (None,{"fields": ("nature_of_injury", "bodily_location","first_aid_details", ("first_aider_name","hospital_name"))}),
            ],

        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'IncidentProperty': {
        'model': IncidentProperty,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'min_num': 1,
            'extra': 0,
            'fieldsets': [
                (None,{"fields": ("property_description", "damage_nature","material_spill_details")}),
            ],

        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'IncidentCost': {
        'model': IncidentCost,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'min_num': 1,
            'extra': 0,
            'fieldsets': [
                (None,{"fields": ("control_cost", "total_cost","other_expenses","currency")}),
            ],

        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'IncidentWitness': {
        'model': IncidentWitness,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'min_num': 1,
            'extra': 0,
        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'IncidentPhoto': {
        'model': IncidentPhoto,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'IncidentAnalysis': {
        'model': IncidentAnalysis,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'min_num': 1,
            'extra': 0,
            'fieldsets': [
                (None,{"fields": ("sequence_of_events",)}),
                ("الاسباب المباشرة Immediate Causes",{"fields": ("unsafe_acts","unsafe_conditions", ("repeated_incident","repeated_incident_reason"))}),
            ],
        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'ContributingFactor': {
        'model': ContributingFactor,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'min_num': 1,
            'extra': 0,
        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'FactorsAssessment': {
        'model': FactorsAssessment,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'min_num': 1,
            'extra': 0,
            'fieldsets': [
                (None,{"fields": (("related_documents_exist", "related_documents_details"),"failed_controls")}),
                (None,{"fields": (
                    ("supervisor_present", "supervisor_presence_reason"),
                    ("supervisor_hazard_competency", "supervisor_hazard_reason"),
                    ("supervisor_controls_competency", "supervisor_controls_reason"),
                    ("person_hazard_competency", "person_hazard_reason"),
                    ("competency_in_controls", "competency_controls_reason"),
                    ("correct_ppe_worn", "ppe_reason"),
                    ("technical_competence", "technical_competence_reason"),
                    ("fatigue_factor", "fatigue_reason"),
                    ("substance_abuse_factor", "substance_abuse_reason"),
                    ("correct_equipment_used", "equipment_reason"),
                    ("equipment_good_condition", "equipment_condition_reason"),
                    ("equipment_inspected", "equipment_inspection_reason"),
                    ("risk_assessment_conducted", "risk_assessment_reason"),
                    ("area_declared_safe", "area_safety_reason"),
                    ("changes_after_declaration", "changes_details"),
                    ("other_root_causes", ),
                )}),
            ],
        },
        'groups': {
            'production_control_auditor':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'AppHSECorrectiveAction': {
        'model': AppHSECorrectiveAction,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
            'view_on_site': False,
            'exclude': ('report', 'state',),
        },
        'groups': {
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'LeasonLearnt': {
        'model': LeasonLearnt,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
            'view_on_site': False,
            'exclude': ('state',),
        },
        'groups': {
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },

}

incident_feedback_model_admin, incident_feedback_inlines = create_main_form(incident_main_class,incident_inline_classes,incident_main_mixins)

admin.site.register(incident_feedback_model_admin.model,incident_feedback_model_admin)
