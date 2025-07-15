from importlib import import_module
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.admin.utils import (
    flatten_fieldsets,
    unquote,
)
from django.contrib.admin import helpers
from django.contrib.admin.options import TO_FIELD_VAR
# from it.models import ItRecommendationForm
from it.models import ITService, ITServiceModification, ITServiceOperation, ITServiceResponsibility, ITServiceSLAAgreement, ITServiceScope
from workflow.admin_utils import create_main_form

class LogMixin:
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

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

class ReadonlyMixin:
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.state  > self.model.STATE_CONFIRMED:
            return ['date','name','department','responsible','requirements_description','product_description']
        return []

#######DevelopmentRequestForm##########
def get_my_inlines(self, request, obj): 
    inlines = super(self.__class__, self).get_inlines(request, obj)
    if obj and obj.state  >= DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION:
        try:
            obj.it_recommendation_form
        except:
            for l in inlines:
                if l.model == ItRecommendationForm:
                    inlines.remove(l)

        try:
            obj.it_rejection_form
        except:
            for l in inlines:
                if l.model == ItRejectionForm:
                    inlines.remove(l)

    return inlines

development_request_main_mixins = [LogMixin,ReadonlyMixin]
models = import_module('it.models')
DevelopmentRequestForm = models.__getattribute__('DevelopmentRequestForm')
development_request_main_class = {
    'model': DevelopmentRequestForm,
    'mixins': [],
    'kwargs': {
        'list_display': ('date', 'department','responsible'),
        'search_fields': ('department','responsible'),
        'list_filter': ('date', 'department', 'responsible'),
        'exclude': ('state',),
        'save_as_continue': False,
        'get_inlines': get_my_inlines
    },
    'groups': {
        'department_manager':{
            'permissions': {
                DevelopmentRequestForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                DevelopmentRequestForm.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_REJECTION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

        'general_manager':{
            'permissions': {
                # DevelopmentRequestForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                DevelopmentRequestForm.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 0},
                DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_REJECTION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

        'it_manager':{
            'permissions': {
                # DevelopmentRequestForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # DevelopmentRequestForm.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_APPROVAL: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_REJECTION: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

        'pqi_manager':{
            'permissions': {
                # DevelopmentRequestForm.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # DevelopmentRequestForm.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # DevelopmentRequestForm.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_APPROVAL: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                # DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_REJECTION: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 1, 'delete': 0, 'view': 1},
                DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

    },
}
# inline_mixins = [LogMixin]
ItRecommendationForm = models.__getattribute__('ItRecommendationForm')
ItRejectionForm = models.__getattribute__('ItRejectionForm')

def get_reject_min_num(self, request,obj=None, **kwargs):
    print(obj)
    if obj and obj.state  == DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_REJECTION:
        return 1
    return 0

development_request_inline_classes = {
    'ItRecommendationForm': {
        'model': ItRecommendationForm,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'department_manager':{
                'permissions': {
                    DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'it_manager':{
                'permissions': {
                    DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_APPROVAL: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'ItRejectionForm': {
        'model': ItRejectionForm,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'get_min_num': get_reject_min_num,
        },
        'groups': {
            'department_manager':{
                'permissions': {
                    DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_REJECTION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'general_manager':{
                'permissions': {
                    DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_REJECTION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'it_manager':{
                'permissions': {
                    DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_REJECTION: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    DevelopmentRequestForm.STATE_IT_MANAGER_STUDING_REJECTION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_CHANGE_REQUEST: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DevelopmentRequestForm.STATE_PQI_MANAGER_APPROVAL: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },

}

# inline_classes = {}

model_admin, inlines = create_main_form(development_request_main_class,development_request_inline_classes,development_request_main_mixins)

admin.site.register(model_admin.model,model_admin)


#######ITService##########

it_service_main_mixins = [LogMixin]
it_service_main_class = {
    'model': ITService,
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
                ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

        'pqi_manager':{
            'permissions': {
                ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

    },
}
# inline_mixins = [LogMixin]

it_service_inline_classes = {
    'ITServiceScope': {
        'model': ITServiceScope,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'ITServiceOperation': {
        'model': ITServiceOperation,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'ITServiceSLAAgreement': {
        'model': ITServiceSLAAgreement,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'ITServiceResponsibility': {
        'model': ITServiceResponsibility,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
        },
        'groups': {
            'it_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'ITServiceModification': {
        'model': ITServiceModification,
        'mixins': [admin.StackedInline],
        'kwargs': {
            'extra': 0,

        },
        'groups': {
            'it_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'pqi_manager':{
                'permissions': {
                    ITService.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    ITService.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    ITService.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },

}

model_admin, inlines = create_main_form(it_service_main_class,it_service_inline_classes,it_service_main_mixins)

admin.site.register(model_admin.model,model_admin)
