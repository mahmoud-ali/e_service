from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

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
        for form in formset.forms:
            if form.cleaned_data.get('DELETE', False):
                if form.instance.pk:
                    form.instance.delete()

        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # New inline object
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()

class TblStateRepresentativeAdmin(admin.ModelAdmin):
    model = TblStateRepresentative
    form = TblStateRepresentativeForm
    list_display = ["state", "name", "user"]
    list_filter = ["state"]
    
admin.site.register(TblStateRepresentative,TblStateRepresentativeAdmin)

class AppHSEPerformanceReportMixin(LogMixin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        # print("User groups",request.user.groups.all())
        if request.user.groups.filter(name__in=("hse_cmpny_department_mngr","hse_cmpny_gm","hse_read_only",)).exists():
            # print("has group hse_cmpny_department_mngr or hse_cmpny_gm")
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
                print("Error",e)

        if request.user.groups.filter(name__in=("production_control_auditor",)).exists():
            try:
                company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=PRODUCTION_STATE_CONFIRMED).values_list('company',flat=True)
                return qs.filter(company__id__in=company_lst)
            except Exception as e:
                print(request.user,e)

        return qs.none() #super().get_queryset(request)

    @admin.display(description=_('Ask AI'))
    def ask_ai_link(self, obj):
        url = reverse('profile:app_hse_performance_ai',args=[obj.id])
        return format_html('<a target="_blank" class="viewlink" href="{url}">'+_('Ask AI')+'</a>',
                    url=url
                )

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if request.user.is_superuser or request.user.groups.filter(name='production_control_auditor').exists():
            if 'approver_name' not in fields:
                fields.extend(['approver_name', 'approver_phone'])
        else:
            fields = [f for f in fields if f not in ('approver_name', 'approver_phone')]
        return fields

report_main_mixins = [AppHSEPerformanceReportMixin,]
report_main_class = {
    'model': AppHSEPerformanceReport,
    'mixins': [],
    'kwargs': {
        'list_display': ("company","license", "year", "month","created_at","state","ask_ai_link"), #,"ask_ai_link"
        'list_filter': ('year', 'month','state','created_at'),
        'readonly_fields':('company','license'),
        'fields': ("company","license", "year", "month","album",("reporter_name","reporter_phone"),),
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
                AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_gm':{
            'permissions': {
                AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        "hse_read_only":{
            "permissions": {
                AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }

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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},                   
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},    
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },  
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    AppHSEPerformanceReport.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    AppHSEPerformanceReport.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1}, 
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    AppHSEPerformanceReport.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
        },
    },
}

report_model_admin, report_inlines = create_main_form(report_main_class,report_inline_classes,report_main_mixins)

admin.site.register(report_model_admin.model,report_model_admin)


##############Corrective actions######################
class CompanyFilter(admin.SimpleListFilter):
    title = _('Company')
    parameter_name = 'company'

    def lookups(self, request, model_admin):
        from company_profile.models import TblCompanyProduction
        qs = model_admin.get_queryset(request)
        report_company_ids = qs.exclude(report=None).values_list('report__company_id', flat=True).distinct()
        incident_company_ids = qs.exclude(incident=None).values_list('incident__company_id', flat=True).distinct()
        all_company_ids = set(report_company_ids) | set(incident_company_ids)
        all_company_ids.discard(None)
        companies = TblCompanyProduction.objects.filter(id__in=all_company_ids).order_by('name_ar')
        return [(c.id, c.__str__()) for c in companies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(report__company_id=self.value()) | Q(incident__company_id=self.value())
            )
        return queryset

class AppHSECorrectiveActionMixin:
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if 'company' not in request.GET:
            from company_profile.models import TblCompanyProduction
            qs = self.get_queryset(request)
            report_company_ids = qs.exclude(report=None).values_list('report__company_id', flat=True).distinct()
            incident_company_ids = qs.exclude(incident=None).values_list('incident__company_id', flat=True).distinct()
            all_company_ids = set(report_company_ids) | set(incident_company_ids)
            all_company_ids.discard(None)
            companies = TblCompanyProduction.objects.filter(id__in=all_company_ids).order_by('name_ar')
            extra_context['show_companies'] = True
            extra_context['company_list'] = companies
            
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        # print("User groups",request.user.groups.all())
        if request.user.groups.filter(name__in=("hse_cmpny_department_mngr","hse_cmpny_gm","hse_read_only",)).exists():
            # print("has group hse_cmpny_department_mngr or hse_cmpny_gm")
            return qs
        
        if request.user.groups.filter(name__in=("hse_cmpny_state_mngr",)).exists():
            try:
                # company_type = request.user.gold_production_state_user.company_type
                original_state = request.user.hse_cmpny_state.state
                companies = TblCompanyProductionLicense.objects.filter(state=original_state).values_list('company',flat=True)
                   
                return qs.filter(
                    Q(report__company__in=companies) | Q(incident__company__in=companies)
                )
            except Exception as e:
                print("Error",e)

        if request.user.groups.filter(name__in=("production_control_auditor",)).exists():
            try:
                company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=PRODUCTION_STATE_CONFIRMED).values_list('company',flat=True)
                return qs.filter(
                    Q(report__company__in=company_lst) | Q(incident__company__in=company_lst)
                    )
            except Exception as e:
                print(request.user,e)

        return qs.none() #super().get_queryset(request)

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
        'list_filter': (CompanyFilter,"from_dt","to_dt",'state'),
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
                AppHSECorrectiveAction.STATE_STATE_MNGR_SUBMIT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_STATE_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
        "hse_read_only":{
            "permissions": {
                AppHSECorrectiveAction.STATE_DEPARTMENT_MNGR_CONFIRM: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppHSECorrectiveAction.STATE_GM_APPROVE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        }
    },
}

corrective_inline_classes = {}

corrective_model_admin, corrective_inlines = create_main_form(corrective_main_class,corrective_inline_classes,corrective_main_mixins)

admin.site.register(corrective_model_admin.model,corrective_model_admin)

##########################Corrective actions feedback############
class AppHSECorrectiveActionFeedbackMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        # print("User groups",request.user.groups.all())
        if request.user.groups.filter(name__in=("hse_cmpny_department_mngr","hse_cmpny_gm","hse_read_only",)).exists():
            # print("has group hse_cmpny_department_mngr or hse_cmpny_gm")
            return qs
        
        if request.user.groups.filter(name__in=("hse_cmpny_state_mngr",)).exists():
            try:
                # company_type = request.user.gold_production_state_user.company_type
                original_state = request.user.hse_cmpny_state.state
                companies = TblCompanyProductionLicense.objects.filter(state=original_state).values_list('company',flat=True)
                   
                return qs.filter(
                    Q(corrective_action__report__company__in=companies) | Q(corrective_action__incident__company__in=companies)
                )
            except Exception as e:
                print("Error",e)

        if request.user.groups.filter(name__in=("production_control_auditor",)).exists():
            try:
                company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=PRODUCTION_STATE_CONFIRMED).values_list('company',flat=True)
                return qs.filter(
                    Q(corrective_action__report__company__in=company_lst) | Q(corrective_action__incident__company__in=company_lst)
                    )
            except Exception as e:
                print(request.user,e)

        return qs.none() #super().get_queryset(request)

corrective_action_feedback_main_mixins = [AppHSECorrectiveActionFeedbackMixin,LogMixin]
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
class IncidentInfoMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        # print("User groups",request.user.groups.all())
        if request.user.groups.filter(name__in=("hse_cmpny_department_mngr","hse_cmpny_gm","hse_read_only",)).exists():
            # print("has group hse_cmpny_department_mngr or hse_cmpny_gm")
            return qs
        
        if request.user.groups.filter(name__in=("hse_cmpny_state_mngr",)).exists():
            try:
                # company_type = request.user.gold_production_state_user.company_type
                original_state = request.user.hse_cmpny_state.state
                companies = TblCompanyProductionLicense.objects.filter(state=original_state).values_list('company',flat=True)
                   
                return qs.filter(
                    company__in=companies
                )
            except Exception as e:
                print("Error",e)

        if request.user.groups.filter(name__in=("production_control_auditor",)).exists():
            try:
                company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=PRODUCTION_STATE_CONFIRMED).values_list('company',flat=True)
                return qs.filter(
                    company__in=company_lst
                    )
            except Exception as e:
                print(request.user,e)

        return qs.none() #super().get_queryset(request)
    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if request.user.is_superuser or request.user.groups.filter(name='production_control_auditor').exists():
            fieldsets.append((
                _("بيانات معتمد التقرير"),
                {"fields": (("approver_name", "approver_phone"),)}
            ))
        return fieldsets

incident_main_mixins = [IncidentInfoMixin,LogMixin]
incident_main_class = {
    'model': IncidentInfo,
    'mixins': [],
    'kwargs': {
        'list_display': ("company", "incident_category", "incident_type","classification","state",),
        'list_filter': ('incident_category','incident_type', 'classification','state'),
        # 'readonly_fields':('company',),
        # 'fields': ("company", "year", "month","album",),
        'fieldsets': [
            (None,{"fields": ("company", ("incident_category","classification"), ("incident_type","other_type_details"))}),
            ("تفاصيل الحادث Details of Incident",{"fields": (("equipment_vehicle_no","client_contractor"), "date_time_occurred","date_time_reported","reported_to","location","incident_description")}),
            ("تفاصيل العملية والمكان في زمن الحادث Location and Operation at Time of Incident",{"fields": ("precise_location", "precise_operation","site_closed_now","site_closed_because_of_incident")}),
            ("بيانات محرر التقرير",{"fields": (("reporter_name","reporter_phone"),)}),
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
                IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_cmpny_department_mngr':{
            'permissions': {
                IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},    
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
        "hse_read_only":{
            "permissions": {
                IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        }
    },
}

def incident_corrective_action_display(self, obj):
    return obj.corrective_action if obj else '-'
incident_corrective_action_display.short_description = _("الإجراء التصحيحي")

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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            }
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
            "hse_read_only":{
                "permissions": {
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
            'show_change_link': True,
            'incident_corrective_action_display': incident_corrective_action_display,
            'readonly_fields': ('incident_corrective_action_display',),
            'fields': ('corrective_action', 'from_dt', 'to_dt',),
        },
        'groups': {
            'hse_cmpny_state_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
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
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 1, 'change': 1, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_department_mngr':{
                'permissions': {
                    IncidentInfo.STATE_SUBMITTED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_cmpny_gm':{
                'permissions': {
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    IncidentInfo.STATE_AUDITOR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    IncidentInfo.STATE_STATE_MNGR_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },

}

incident_feedback_model_admin, incident_feedback_inlines = create_main_form(incident_main_class,incident_inline_classes,incident_main_mixins)

admin.site.register(incident_feedback_model_admin.model,incident_feedback_model_admin)



from hse_companies.models import (
    TblCompanyEvaluationSession,
    TblCompanyEvaluationEnvironment,
    TblCompanyEvaluationSafety,
    TblCompanyEvaluationGeneral
)

class AppHSEEvaluationSessionMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.groups.filter(name__in=("hse_cmpny_department_mngr", "hse_cmpny_gm", "hse_read_only")).exists():
            return qs
        
        if request.user.groups.filter(name__in=("hse_cmpny_state_mngr",)).exists():
            try:
                original_state = request.user.hse_cmpny_state.state
                companies = TblCompanyProductionLicense.objects.filter(state=original_state).values_list('company', flat=True)
                return qs.filter(company__in=companies)
            except Exception as e:
                print("Error Evaluation State Mngr:", e)

        if request.user.groups.filter(name__in=("production_control_auditor",)).exists():
            try:
                company_lst = request.user.moragib_list.moragib_distribution.goldproductionuserdetail_set.filter(master__state=PRODUCTION_STATE_CONFIRMED).values_list('company', flat=True)
                return qs.filter(company__id__in=company_lst)
            except Exception as e:
                print("Error Evaluation Auditor:", e)

        return qs.none()

class TblCompanyEvaluationEnvironmentInline(admin.StackedInline):
    model = TblCompanyEvaluationEnvironment
    extra = 1
    max_num = 1

class TblCompanyEvaluationSafetyInline(admin.StackedInline):
    model = TblCompanyEvaluationSafety
    extra = 1
    max_num = 1

class TblCompanyEvaluationGeneralInline(admin.StackedInline):
    model = TblCompanyEvaluationGeneral
    extra = 1
    max_num = 1

class TblCompanyEvaluationSessionAdmin(AppHSEEvaluationSessionMixin, admin.ModelAdmin):
    list_display = ('company', 'evaluation_date', 'state', 'locality', 'total_score_display')
    list_filter = ('evaluation_date', 'state')

    @admin.display(description=_("النتيجة الإجمالية"))
    def total_score_display(self, obj):
        scores = []
        try:
            scores.append(obj.environment.get_average_score())
        except Exception:
            pass
        try:
            scores.append(obj.safety.get_average_score())
        except Exception:
            pass
        try:
            scores.append(obj.general.get_average_score())
        except Exception:
            pass

        if not scores:
            return '-'

        avg = round(sum(scores) / len(scores), 2)
        pct = round((avg - 1) / 2 * 100) if avg > 0 else 0

        if pct > 70:
            color = '#28a745'  # أخضر - ممتاز
        elif pct >= 50:
            color = '#ffc107'  # أصفر - متوسط
        else:
            color = '#dc3545'  # أحمر - ضعيف

        return format_html(
            '<span style="color:{color}; font-weight:bold; font-size:1.05em;">{pct}%</span>',
            color=color, pct=pct
        )
    search_fields = ('company__name_ar', 'company__name_en')
    autocomplete_fields = ['company']
    inlines = [
        TblCompanyEvaluationEnvironmentInline,
        TblCompanyEvaluationSafetyInline,
        TblCompanyEvaluationGeneralInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            for field in ['company', 'state', 'locality']:
                if field in form.base_fields:
                    form.base_fields[field].widget.can_add_related = False
                    form.base_fields[field].widget.can_change_related = False
                    form.base_fields[field].widget.can_delete_related = False
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and request.user.groups.filter(name="hse_cmpny_state_mngr").exists():
            try:
                original_state = request.user.hse_cmpny_state.state
                if db_field.name == "state":
                    kwargs["queryset"] = db_field.related_model.objects.filter(id=original_state.id)
                elif db_field.name == "locality":
                    kwargs["queryset"] = db_field.related_model.objects.filter(state=original_state)
            except Exception as e:
                print("Error formfield_for_foreignkey for hse_cmpny_state_mngr:", e)
                if db_field.name in ("state", "locality"):
                    kwargs["queryset"] = db_field.related_model.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        for instance in formset.deleted_objects:
            instance.delete()
        formset.save_m2m()

admin.site.register(TblCompanyEvaluationSession, TblCompanyEvaluationSessionAdmin)

from company_profile.admin import TblCompanyProductionAdmin
from company_profile.models import TblCompany, TblCompanyProductionLicense
from django.db import models

def hse_tbl_company_production_get_queryset(self, request):
    qs = super(TblCompanyProductionAdmin, self).get_queryset(request)

    if (
        request.user.is_superuser
        or request.user.groups.filter(name__in=("hse_cmpny_department_mngr", "hse_cmpny_gm", "hse_read_only")).exists()
    ):
        pass
    elif request.user.groups.filter(name__in=("hse_cmpny_state_mngr",)).exists():
        try:
            original_state = request.user.hse_cmpny_state.state
            companies = TblCompanyProductionLicense.objects.filter(state=original_state).values_list('company', flat=True)
            qs = qs.filter(id__in=companies)
        except Exception as e:
            print("Error TblCompanyProductionAdmin get_queryset for hse_cmpny_state_mngr:", e)
            qs = qs.none()
    else:
        company_types = []
        if request.user.groups.filter(name="company_type_entaj").exists():
            company_types += [TblCompany.COMPANY_TYPE_ENTAJ]
        if request.user.groups.filter(name="company_type_mokhalfat").exists():
            company_types += [TblCompany.COMPANY_TYPE_MOKHALFAT]
        if request.user.groups.filter(name="company_type_emtiaz").exists():
            company_types += [TblCompany.COMPANY_TYPE_EMTIAZ]
        if request.user.groups.filter(name="company_type_sageer").exists():
            company_types += [TblCompany.COMPANY_TYPE_SAGEER]

        qs = qs.filter(company_type__in=company_types)

    qs = qs.prefetch_related(models.Prefetch("tblcompanyproductionlicense_set"))
    
    is_changelist = request.resolver_match and request.resolver_match.url_name.endswith('_changelist')
    show_inactive = request.GET.get('show_inactive') == '1'
    
    if is_changelist and not (show_inactive or request.GET.get('q')):
        qs = qs.exclude(status__name__in=["منتهية",  "ملغية"])

    return qs

TblCompanyProductionAdmin.get_queryset = hse_tbl_company_production_get_queryset

def hse_tbl_company_production_has_view_permission(self, request, obj=None):
    if request and request.user and request.user.is_authenticated:
        if request.user.groups.filter(name__in=("hse_cmpny_state_mngr", "hse_cmpny_department_mngr", "hse_cmpny_gm", "hse_read_only")).exists():
            return True
    return super(TblCompanyProductionAdmin, self).has_view_permission(request, obj)

TblCompanyProductionAdmin.has_view_permission = hse_tbl_company_production_has_view_permission

def hse_tbl_company_production_get_fieldsets(self, request, obj=None):
    fieldsets = super(TblCompanyProductionAdmin, self).get_fieldsets(request, obj)
    if request.user and not request.user.is_superuser:
        if request.user.groups.filter(name__in=("hse_cmpny_state_mngr", "hse_cmpny_department_mngr", "hse_cmpny_gm", "hse_read_only")).exists():
            new_fieldsets = []
            for title, fs_options in fieldsets:
                fields = fs_options.get('fields', [])
                flat_fields = []
                for f in fields:
                    if isinstance(f, (list, tuple)):
                        flat_fields.extend(f)
                    else:
                        flat_fields.append(f)
                if any(x in flat_fields for x in ("website", "email", "manager_name", "manager_phone", "rep_name", "rep_phone", "address")):
                    continue
                new_fieldsets.append((title, fs_options))
            return new_fieldsets
    return fieldsets

TblCompanyProductionAdmin.get_fieldsets = hse_tbl_company_production_get_fieldsets



