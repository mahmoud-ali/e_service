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
# from it.models import DevelopmentRequestForm
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

    # def has_delete_permission(self, request, obj=None):        
    #     return False

####global run##########

main_mixins = [LogMixin]
models = import_module('it.models')
DevelopmentRequestForm = models.__getattribute__('DevelopmentRequestForm')
main_class = {
    'model': DevelopmentRequestForm,
    'mixins': [],
    'kwargs': {
        'list_display': ('date', 'department','responsible'),
        'search_fields': ('department','responsible'),
        'list_filter': ('date', 'department', 'responsible'),
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': (
        {
            'name': 'department_manager',
            'states': (DevelopmentRequestForm.STATE_DRAFT,DevelopmentRequestForm.STATE_CONFIRMED,DevelopmentRequestForm.STATE_APPROVED,DevelopmentRequestForm.STATE_IT_MANAGER_RECOMMENDATION,DevelopmentRequestForm.STATE_PCI_MANAGER_APPROVAL),
            'add':1,
            'change':1, 
            'delete':1, 
            'view':1,
        },
    ),
}

# inline_mixins = [LogMixin]
# inline_classes = {
#     'TransferRelocationFormData': {
#         'model': TransferRelocationFormData,
#         'mixins': [admin.TabularInline],
#         'kwargs': {
#             'form': TransferRelocationFormDataForm,
#             'fk_name': 'basic_form',
#             'readonly_fields': ['raw_weight', 'allow_count'],
#             'extra': 1,
#         },
#         'groups': (
#             {
#                 'name': 'sswg_manager',
#                 'states': (BasicForm.STATE_1,BasicForm.STATE_2,BasicForm.STATE_3,BasicForm.STATE_4,BasicForm.STATE_5,BasicForm.STATE_6,BasicForm.STATE_7,BasicForm.STATE_8,BasicForm.STATE_9,BasicForm.STATE_10,),
#                 'add':1,
#                 'change':1, 
#                 'delete':1, 
#                 'view':1,
#             },
#             {
#                 'name': 'sswg_secretary',
#                 'states': (BasicForm.STATE_1,BasicForm.STATE_2,BasicForm.STATE_3,BasicForm.STATE_4,BasicForm.STATE_5,BasicForm.STATE_6,BasicForm.STATE_7,BasicForm.STATE_8,BasicForm.STATE_9,BasicForm.STATE_10,),
#                 'add':1,
#                 'change':1, 
#                 'delete':0, 
#                 'view':1,
#             },
#         ),
#     },
# }

inline_classes = {}

model_admin, inlines = create_main_form(main_class,inline_classes,main_mixins)

admin.site.register(model_admin.model,model_admin)
