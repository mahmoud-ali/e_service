from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from hse_traditional.models import Achievement, ArrangementOfMarkets, EnvironmentalInspection, EnvironmentalRequirements, HseTraditionalAccident, HseTraditionalAccidentDamage, HseTraditionalAccidentInjury, HseTraditionalAccidentWho, HseTraditionalAccidentWhy, HseTraditionalCorrectiveAction, HseTraditionalCorrectiveActionFinalDecision, HseTraditionalCorrectiveActionReccomendation, HseTraditionalNearMiss, HseTraditionalNearMissWho, HseTraditionalNearMissWhy, HseTraditionalReport, QuickEmergencyTeam, TrainingAwareness, WasteManagement
from workflow.admin_utils import create_main_form

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

main_mixins = [LogMixin]
main_class = {
    'model': HseTraditionalReport,
    'mixins': [],
    'kwargs': {
        # 'list_display': ('date', 'department','responsible'),
        # 'search_fields': ('department','responsible'),
        # 'list_filter': ('date', 'department', 'responsible'),
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': {
        'it_manager':{
            'permissions': {
                HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

        'pqi_manager':{
            'permissions': {
                HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

    },
}
inline_mixins = [LogMixin]

inline_classes = {
    'EnvironmentalInspection': {
        'model': EnvironmentalInspection,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },

}

# inline_classes = {}

model_admin, inlines = create_main_form(main_class,inline_classes,main_mixins)

admin.site.register(model_admin.model,model_admin)


##########Accidents################
main_mixins = [LogMixin]
main_class = {
    'model': HseTraditionalAccident,
    'mixins': [],
    'kwargs': {
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': {
        'it_manager':{
            'permissions': {
                HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'pqi_manager':{
            'permissions': {
                HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

inline_mixins = [LogMixin]

inline_classes = {
    'HseTraditionalAccidentWho': {
        'model': HseTraditionalAccidentWho,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    HseTraditionalAccident.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalAccident.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalAccident.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
}

model_admin, inlines = create_main_form(main_class, inline_classes, main_mixins)

admin.site.register(model_admin.model, model_admin)

##########Near misses################
main_mixins = [LogMixin]
main_class = {
    'model': HseTraditionalNearMiss,
    'mixins': [],
    'kwargs': {
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': {
        'it_manager':{
            'permissions': {
                HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'pqi_manager':{
            'permissions': {
                HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

inline_mixins = [LogMixin]

inline_classes = {
    'HseTraditionalNearMissWho': {
        'model': HseTraditionalNearMissWho,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
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
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    HseTraditionalNearMiss.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalNearMiss.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalNearMiss.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
}

model_admin, inlines = create_main_form(main_class, inline_classes, main_mixins)

admin.site.register(model_admin.model, model_admin)


##########Corrective action################
main_mixins = [LogMixin]
main_class = {
    'model': HseTraditionalCorrectiveAction,
    'mixins': [],
    'kwargs': {
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': {
        'it_manager':{
            'permissions': {
                HseTraditionalCorrectiveAction.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'pqi_manager':{
            'permissions': {
                HseTraditionalCorrectiveAction.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                HseTraditionalCorrectiveAction.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
    },
}

inline_mixins = []
inline_classes = {
    'HseTraditionalCorrectiveActionReccomendation': {
        'model': HseTraditionalCorrectiveActionReccomendation,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'HseTraditionalCorrectiveActionFinalDecision': {
        'model': HseTraditionalCorrectiveActionFinalDecision,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    HseTraditionalReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    HseTraditionalReport.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    HseTraditionalReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },

}
model_admin, inlines = create_main_form(main_class, inline_classes, main_mixins)

admin.site.register(model_admin.model, model_admin)
