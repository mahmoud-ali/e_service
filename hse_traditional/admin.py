from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from hse_traditional.forms import HseTraditionalCorrectiveActionForm, TblStateRepresentativeForm
from hse_traditional.models import Achievement, ArrangementOfMarkets, EnvironmentalInspection, EnvironmentalRequirements, HseTraditionalAccident, HseTraditionalAccidentDamage, HseTraditionalAccidentInjury, HseTraditionalAccidentWho, HseTraditionalAccidentWhy, HseTraditionalCorrectiveAction, HseTraditionalCorrectiveActionFinalDecision, HseTraditionalCorrectiveActionReccomendation, HseTraditionalNearMiss, HseTraditionalNearMissWho, HseTraditionalNearMissWhy, HseTraditionalReport, ImmediateAction, QuickEmergencyTeam, TblStateRepresentative, TrainingAwareness, WasteManagement
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
                # HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
        'list_display': ('type', 'what','source_state','state'),
        'list_filter': ('type', 'source_state','state'),
        'exclude': ('state','source_state'),
        'save_as_continue': False,
    },
    'groups': {
        'hse_tra_state_employee':{
            'permissions': {
                HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
                # HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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
        'list_display': ('source_accident','source_near_miss','source_state','state'),
        'list_filter': ('source_accident','source_near_miss','source_state','state'),
        'exclude': ('state','source_state'),
        'get_form': get_corrective_action_form,
        'save_as_continue': False,
    },
    'groups': {
        'hse_tra_state_employee':{
            'permissions': {
                HseTraditionalCorrectiveAction.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
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

        },
    },

}
model_admin, inlines = create_main_form(corrective_action_main_class, corrective_action_inline_classes, corrective_action_main_mixins)

admin.site.register(model_admin.model, model_admin)
