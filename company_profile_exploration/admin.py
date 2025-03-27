from django.contrib import admin
from company_profile_exploration.models.work_plan import AppWorkPlan, Brief, ContractRecommendation, Coordinate, Equipment, LkpPhase, LogisticsAdministration, Other, Phase, SamplePreparation, StaffInformation, SubsurfaceExplorationActivitie, SurfaceExplorationActivitie, TargetCommodity, TechnicalRecommendation, Todo
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

class AppWorkPlanMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.groups.filter(name__in=("exploration_technical",)).exists():
            ids = []
            for obj in qs:
                if request.user.groups.filter(name__in=("exploration_technical_development",)).exists() and obj.company.state in []:
                    ids.append(obj.id)
                
                if request.user.groups.filter(name__in=("exploration_technical_exploration",)).exists() and obj.company.state in []:
                    ids.append(obj.id)
                    
            qs = qs.filter(id__in=ids)

        return qs

work_plan_main_mixins = [AppWorkPlanMixin,LogMixin]
work_plan_main_class = {
    'model': AppWorkPlan,
    'mixins': [],
    # 'static_inlines': [],
    'kwargs': {
        # 'list_display': ('year', 'month','source_state','state'),
        # 'list_filter': ('year', 'month','source_state','state'),
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': {
        'exploration_gm':{
            'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

    },
}

work_plan_inline_classes = {
    'TargetCommodity': {
        'model': TargetCommodity,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'Coordinate': {
        'model': Coordinate,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'Brief': {
        'model': Brief,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'Phase': {
        'model': Phase,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'StaffInformation': {
        'model': StaffInformation,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'LogisticsAdministration': {
        'model': LogisticsAdministration,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'Equipment': {
        'model': Equipment,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'SurfaceExplorationActivitie': {
        'model': SurfaceExplorationActivitie,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'SubsurfaceExplorationActivitie': {
        'model': SubsurfaceExplorationActivitie,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'SamplePreparation': {
        'model': SamplePreparation,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'Other': {
        'model': Other,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'ContractRecommendation': {
        'model': ContractRecommendation,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'TechnicalRecommendation': {
        'model': TechnicalRecommendation,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_GM_DECISION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },
    'Todo': {
        'model': Todo,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'exploration_gm':{
                'permissions': {
                AppWorkPlan.STATE_GM_DECISION: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                AppWorkPlan.STATE_REVIEW_CONTRACT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_TECHNICAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REVIEW_COMPANY: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_ACCEPTANCE_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_ACCEPTANCE_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_RELEASE_REJECTION_CERTIFICATE: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                AppWorkPlan.STATE_REJECTION_CERTIFICATE_RELEASED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        },
    },

}

work_plan_admin, inlines = create_main_form(work_plan_main_class,work_plan_inline_classes,work_plan_main_mixins)

admin.site.register(work_plan_admin.model,work_plan_admin)

class LkpPhaseAdmin(LogMixin,admin.ModelAdmin):
    model = LkpPhase

admin.site.register(LkpPhase,LkpPhaseAdmin)
