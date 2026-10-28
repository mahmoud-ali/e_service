from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from hse_traditional.forms import HseTraditionalCorrectiveActionForm, MonthlyPerformanceReportForm, TblStateRepresentativeForm
from hse_traditional.models import Achievement, ArrangementOfMarkets, EnvironmentalInspection, EnvironmentalRequirements, HseTraditionalAccident, HseTraditionalAccidentDamage, HseTraditionalAccidentInjury, HseTraditionalAccidentManagerComment, HseTraditionalAccidentWho, HseTraditionalAccidentWhy, HseTraditionalCorrectiveAction, HseTraditionalCorrectiveActionFinalDecision, HseTraditionalCorrectiveActionReccomendation, HseTraditionalNearMiss, HseTraditionalNearMissWho, HseTraditionalNearMissWhy, HseTraditionalReport, ImmediateAction, NotifiedUser, QuickEmergencyTeam, TblStateRepresentative, TrainingAwareness, WasteManagement, HseTraditionalInitialIncidentReport, MonthlyPerformanceReport, MonthlyPerformanceHseRequirements, MonthlyPerformanceAdminControl, MonthlyPerformanceMission, MonthlyPerformanceObstacle
from workflow.admin_utils import create_main_form

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

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.groups.filter(name='hse_read_only').exists():
            return qs

        try:
            source_state = request.user.hse_tra_state.state
            qs = qs.filter(source_state=source_state)
        except:
            pass
        return qs

class TblStateRepresentativeAdmin(admin.ModelAdmin):
    model = TblStateRepresentative
    form = TblStateRepresentativeForm
    list_display = ["state", "name", "user"]
    list_filter = ["state"]
    
admin.site.register(TblStateRepresentative,TblStateRepresentativeAdmin)

report_main_mixins = [LogMixin]
report_main_class = {
    'model': HseTraditionalReport,
    'mixins': [],
    'kwargs': {
        'list_display': ('year', 'month','source_state','state'),
        'list_filter': ('year', 'month','source_state','state'),
        'exclude': ('state','source_state'),
        'save_as_continue': False,
    },
    'groups': {
        'hse_tra_state_employee':{
            'permissions': {
                HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_manager':{
            'permissions': {
                HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_gm':{
            'permissions': {
                HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        "hse_read_only":{
            "permissions": {
                HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

    },
}
# inline_mixins = [LogMixin]

report_inline_classes = {
    'EnvironmentalInspection': {
        'model': EnvironmentalInspection,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'WasteManagement': {
        'model': WasteManagement,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'TrainingAwareness': {
        'model': TrainingAwareness,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'ArrangementOfMarkets': {
        'model': ArrangementOfMarkets,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'EnvironmentalRequirements': {
        'model': EnvironmentalRequirements,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'QuickEmergencyTeam': {
        'model': QuickEmergencyTeam,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 0,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'Achievement': {
        'model': Achievement,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 0,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },

}

model_admin, inlines = create_main_form(report_main_class,report_inline_classes,report_main_mixins)

admin.site.register(model_admin.model,model_admin)


##########Accidents################
accident_main_mixins = [LogMixin]
accident_main_class = {
    'model': HseTraditionalAccident,
    'mixins': [],
    'kwargs': {
        'list_display': ('type', 'what','category','source_state','state'),
        'list_filter': ('type','category', 'source_state','state'),
        'exclude': ('state','source_state'),
        'save_as_continue': False,
    },
    'groups': {
        'hse_tra_state_employee':{
            'permissions': {
                HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_manager':{
            'permissions': {
                HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_gm':{
            'permissions': {
                HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'general_manager':{
            'permissions': {
                HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        "hse_read_only":{
            "permissions": {
                HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

# inline_mixins = [LogMixin]

accident_inline_classes = {
    'HseTraditionalAccidentWho': {
        'model': HseTraditionalAccidentWho,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'HseTraditionalAccidentWhy': {
        'model': HseTraditionalAccidentWhy,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'HseTraditionalAccidentInjury': {
        'model': HseTraditionalAccidentInjury,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 0,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'HseTraditionalAccidentDamage': {
        'model': HseTraditionalAccidentDamage,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 0,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'ImmediateAction': {
        'model': ImmediateAction,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'HseTraditionalAccidentManagerComment': {
        'model': HseTraditionalAccidentManagerComment,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    # HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
}

model_admin, inlines = create_main_form(accident_main_class, accident_inline_classes, accident_main_mixins)

admin.site.register(model_admin.model, model_admin)

##########Near misses################
near_miss_main_mixins = [LogMixin]
near_miss_main_class = {
    'model': HseTraditionalNearMiss,
    'mixins': [],
    'kwargs': {
        'list_display': ('type', 'what','source_state','state'),
        'list_filter': ('type', 'source_state','state'),
        'exclude': ('state','source_state'),
        'save_as_continue': False,
    },
    'groups': {
        'hse_tra_state_employee':{
            'permissions': {
                HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_manager':{
            'permissions': {
                HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_gm':{
            'permissions': {
                HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        "hse_read_only":{
            "permissions": {
                HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

# inline_mixins = [LogMixin]

near_miss_inline_classes = {
    'HseTraditionalNearMissWho': {
        'model': HseTraditionalNearMissWho,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'HseTraditionalNearMissWhy': {
        'model': HseTraditionalNearMissWhy,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'hse_tra_state_employee':{
                'permissions': {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_manager':{
                'permissions': {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
}

model_admin, inlines = create_main_form(near_miss_main_class, near_miss_inline_classes, near_miss_main_mixins)

admin.site.register(model_admin.model, model_admin)


##########Corrective action################

def get_corrective_action_form(self, request, obj=None, **kwargs):

    HseTraditionalCorrectiveActionForm.request = request

    return HseTraditionalCorrectiveActionForm

corrective_action_main_mixins = [LogMixin]
corrective_action_main_class = {
    'model': HseTraditionalCorrectiveAction,
    'mixins': [],
    'kwargs': {
        'list_display': ('source_report','source_accident','source_near_miss','source_state','state'),
        'list_filter': ('source_report','source_accident','source_near_miss','source_state','state'),
        'exclude': ('state','source_state'),
        'get_form': get_corrective_action_form,
        'save_as_continue': False,
    },
    'groups': {
        'hse_tra_state_employee':{
            'permissions': {
                HseTraditionalCorrectiveAction.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_manager':{
            'permissions': {
                HseTraditionalCorrectiveAction.STATE_CONFIRMED1: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_gm':{
            'permissions': {
                HseTraditionalCorrectiveAction.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_CONFIRMED2: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        "hse_read_only":{
            "permissions": {
                HseTraditionalCorrectiveAction.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

# inline_mixins = []
corrective_action_inline_classes = {
    'HseTraditionalCorrectiveActionReccomendation': {
        'model': HseTraditionalCorrectiveActionReccomendation,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            # 'hse_tra_state_employee':{
            #     'permissions': {
            #         HseTraditionalCorrectiveAction.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
            #         HseTraditionalCorrectiveAction.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            #         HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            #     },
            # },
            'hse_tra_manager':{
                'permissions': {
                    # HseTraditionalCorrectiveAction.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 0},
                    HseTraditionalCorrectiveAction.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_CONFIRMED2: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    # HseTraditionalCorrectiveAction.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalCorrectiveAction.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'HseTraditionalCorrectiveActionFinalDecision': {
        'model': HseTraditionalCorrectiveActionFinalDecision,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            # 'hse_tra_state_employee':{
            #     'permissions': {
            #         HseTraditionalCorrectiveAction.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
            #         HseTraditionalCorrectiveAction.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            #         HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            #     },
            # },
            'hse_tra_manager':{
                'permissions': {
                    # HseTraditionalCorrectiveAction.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'hse_tra_gm':{
                'permissions': {
                    # HseTraditionalCorrectiveAction.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    # HseTraditionalCorrectiveAction.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_CONFIRMED2: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            "hse_read_only":{
                "permissions": {
                    HseTraditionalCorrectiveAction.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },

}
model_admin, inlines = create_main_form(corrective_action_main_class, corrective_action_inline_classes, corrective_action_main_mixins)

admin.site.register(model_admin.model, model_admin)

initial_incident_main_mixins = [LogMixin]
initial_incident_main_class = {
    'model': HseTraditionalInitialIncidentReport,
    'mixins': [],
    'kwargs': {
        'list_display': ('type', 'incident_date', 'incident_time', 'source_state', 'locality', 'market_mine', 'result', 'state'),
        'list_filter': ('type', 'classification', 'result', 'source_state', 'state'),
        'exclude': ('state','source_state'),
        'save_as_continue': False,
    },
    'groups': {
        'hse_tra_state_employee':{
            'permissions': {
                HseTraditionalInitialIncidentReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalInitialIncidentReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalInitialIncidentReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_manager':{
            'permissions': {
                HseTraditionalInitialIncidentReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalInitialIncidentReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_gm':{
            'permissions': {
                HseTraditionalInitialIncidentReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalInitialIncidentReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'general_manager':{
            'permissions': {
                HseTraditionalInitialIncidentReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalInitialIncidentReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        "hse_read_only":{
            "permissions": {
                HseTraditionalInitialIncidentReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalInitialIncidentReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

model_admin_initial, inlines_initial = create_main_form(initial_incident_main_class, {}, initial_incident_main_mixins)
admin.site.register(model_admin_initial.model, model_admin_initial)

class NotifiedUserAdmin(admin.ModelAdmin):
    model = NotifiedUser
    list_display = ["name", ]

admin.site.register(NotifiedUser,NotifiedUserAdmin)


class MonthlyPerformanceLogMixin:
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
            try:
                obj.source_state = request.user.hse_tra_state.state
            except Exception:
                pass
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):       
        for f in formset.forms:
            if f.cleaned_data.get('DELETE', False):
                if f.instance.pk:
                    f.instance.delete()
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name='hse_read_only').exists():
            return qs
        try:
            source_state = request.user.hse_tra_state.state
            qs = qs.filter(source_state=source_state)
        except:
            pass
        return qs

    def get_exclude(self, request, obj=None):
        return ('state',)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj) or [])
        has_state = False
        try:
            _ = request.user.hse_tra_state.state
            has_state = True
        except Exception:
            pass

        if has_state and 'source_state' not in readonly:
            readonly.append('source_state')

        return readonly

    def get_form(self, request, obj=None, **kwargs):
        MonthlyPerformanceReportForm.request = request
        kwargs['form'] = MonthlyPerformanceReportForm
        return super().get_form(request, obj, **kwargs)



def _perf_inline_can_edit(request, obj):
    if request.user.is_superuser:
        return True
    if obj is None:
        return request.user.groups.filter(name='hse_tra_state_employee').exists()
    return (
        obj.state == MonthlyPerformanceReport.STATE_DRAFT
        and request.user.groups.filter(name='hse_tra_state_employee').exists()
    )


class MonthlyPerformanceHseRequirementsInline(admin.StackedInline):
    model = MonthlyPerformanceHseRequirements
    extra = 0
    min_num = 1
    max_num = 1
    verbose_name = _("جدول الموقف الكلي لاشتراطات البيئة والسلامة والصحة المهنية")
    verbose_name_plural = _("جدول الموقف الكلي لاشتراطات البيئة والسلامة والصحة المهنية")

    def has_add_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_change_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_delete_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_view_permission(self, request, obj=None):
        return True


class MonthlyPerformanceAdminControlInline(admin.StackedInline):
    model = MonthlyPerformanceAdminControl
    extra = 0
    min_num = 1
    max_num = 1
    verbose_name = _("جدول الرقابة الإدارية على البيئة والسلامة والصحة المهنية")
    verbose_name_plural = _("جدول الرقابة الإدارية على البيئة والسلامة والصحة المهنية")

    def has_add_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_change_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_delete_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_view_permission(self, request, obj=None):
        return True


class MonthlyPerformanceMissionInline(admin.StackedInline):
    model = MonthlyPerformanceMission
    extra = 1
    min_num = 0
    verbose_name = _("مامورية / زيارة / اجتماع مع أصحاب المصلحة")
    verbose_name_plural = _("ماموريات وزيارات واجتماعات مع أصحاب المصلحة")

    def has_add_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_change_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_delete_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_view_permission(self, request, obj=None):
        return True


class MonthlyPerformanceObstacleInline(admin.StackedInline):
    model = MonthlyPerformanceObstacle
    extra = 1
    min_num = 0
    verbose_name = _("معوق الأداء")
    verbose_name_plural = _("معوقات الأداء خلال فترة التقرير")

    def has_add_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_change_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_delete_permission(self, request, obj=None):
        return _perf_inline_can_edit(request, obj)

    def has_view_permission(self, request, obj=None):
        return True


perf_report_main_mixins = [MonthlyPerformanceLogMixin]
perf_report_main_class = {
    'model': MonthlyPerformanceReport,
    'mixins': [],
    'kwargs': {
        'list_display': ('year', 'month', 'source_state', 'soag', 'state'),
        'list_filter': ('year', 'month', 'source_state', 'state'),
        'exclude': ('state', 'source_state'),
        'save_as_continue': False,
    },
    'static_inlines': [
        MonthlyPerformanceHseRequirementsInline,
        MonthlyPerformanceAdminControlInline,
        MonthlyPerformanceMissionInline,
        MonthlyPerformanceObstacleInline,
    ],
    'groups': {
        'hse_tra_state_employee': {
            'permissions': {
                MonthlyPerformanceReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                MonthlyPerformanceReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                MonthlyPerformanceReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_manager': {
            'permissions': {
                MonthlyPerformanceReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                MonthlyPerformanceReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_tra_gm': {
            'permissions': {
                MonthlyPerformanceReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                MonthlyPerformanceReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'hse_read_only': {
            'permissions': {
                MonthlyPerformanceReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                MonthlyPerformanceReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}


perf_model_admin, perf_inlines = create_main_form(perf_report_main_class, {}, perf_report_main_mixins)
admin.site.register(perf_model_admin.model, perf_model_admin)





