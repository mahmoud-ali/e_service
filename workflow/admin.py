from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.admin.utils import (
    flatten_fieldsets,
    unquote,
)
from django.contrib.admin import helpers
from django.contrib.admin.options import TO_FIELD_VAR
from sswg.forms import TransferRelocationFormDataForm
from sswg.models import CompanyDetails, MmAceptanceData, TransferRelocationFormData, SSMOData, BasicForm, MOCSData, CBSData, SmrcNoObjectionData
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

    def has_delete_permission(self, request, obj=None):
        # if obj and obj.state == BasicForm.STATE_1:
        #     return True
        
        return False

####global run##########

main_mixins = [LogMixin]
main_class = {
    'model': BasicForm,
    'mixins': [],
    'kwargs': {
        'list_display': ('sn_no', 'date'),
        'search_fields': ('sn_no', 'date'),
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': (
        {
            'name': 'sswg_manager',
            'states': (BasicForm.STATE_1,BasicForm.STATE_2,BasicForm.STATE_3,BasicForm.STATE_4,BasicForm.STATE_5,BasicForm.STATE_6,BasicForm.STATE_7,BasicForm.STATE_8,BasicForm.STATE_9,BasicForm.STATE_10,),
            'add':1,
            'change':1, 
            'delete':1, 
            'view':1,
        },
        {
            'name': 'sswg_secretary',
            'states': (BasicForm.STATE_1,),
            'add':1,
            'change':1, 
            'delete':1, 
            'view':1,
        },
    ),
}

inline_mixins = [LogMixin]
inline_classes = {
    'TransferRelocationFormData': {
        'model': TransferRelocationFormData,
        'kwargs': {
            'form': TransferRelocationFormDataForm,
            'mixins': [admin.TabularInline],
            'fk_name': 'basic_form',
            'readonly_fields': ['raw_weight', 'allow_count'],
            'extra': 1,
        },
        'groups': (
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_1,BasicForm.STATE_2,BasicForm.STATE_3,BasicForm.STATE_4,BasicForm.STATE_5,BasicForm.STATE_6,BasicForm.STATE_7,BasicForm.STATE_8,BasicForm.STATE_9,BasicForm.STATE_10,),
                'add':1,
                'change':1, 
                'delete':1, 
                'view':1,
            },
            {
                'name': 'sswg_secretary',
                'states': (BasicForm.STATE_1,BasicForm.STATE_2,BasicForm.STATE_3,BasicForm.STATE_4,BasicForm.STATE_5,BasicForm.STATE_6,BasicForm.STATE_7,BasicForm.STATE_8,BasicForm.STATE_9,BasicForm.STATE_10,),
                'add':1,
                'change':1, 
                'delete':0, 
                'view':1,
            },
        ),
    },
    'CompanyDetails': {
        'model': CompanyDetails,
        'kwargs': {
            'fk_name': 'basic_form',
            'extra': 1,
            'readonly_fields': ['name', 'surrogate_name', 'surrogate_id_type', 'surrogate_id_val', 'surrogate_id_phone'],
        },
        'groups': (
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_1,BasicForm.STATE_2,BasicForm.STATE_3,BasicForm.STATE_4,BasicForm.STATE_5,BasicForm.STATE_6,BasicForm.STATE_7,BasicForm.STATE_8,BasicForm.STATE_9,BasicForm.STATE_10,),
                'add':1,
                'change':1, 
                'delete':1, 
                'view':1,
            },
            {
                'name': 'sswg_secretary',
                'states': (BasicForm.STATE_1,BasicForm.STATE_2,BasicForm.STATE_3,BasicForm.STATE_4,BasicForm.STATE_5,BasicForm.STATE_6,BasicForm.STATE_7,BasicForm.STATE_8,BasicForm.STATE_9,BasicForm.STATE_10,),
                'add':1,
                'change':1, 
                'delete':0, 
                'view':1,
            },
        ),
    },
    'SSMOData': {
        'model': SSMOData,
        'kwargs': {
            'fk_name': 'basic_form',
            'extra': 1,
        },
        'groups': (
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_3,BasicForm.STATE_4,BasicForm.STATE_5,BasicForm.STATE_6,BasicForm.STATE_7,BasicForm.STATE_8,BasicForm.STATE_9,BasicForm.STATE_10,),
                'add':1,
                'change':1, 
                'delete':1, 
                'view':1,
            },
        ),
    },
    'SmrcNoObjectionData': {
        'model': SmrcNoObjectionData,
        'kwargs': {
            'fk_name': 'basic_form',
            'extra': 1,
        },
        'groups': (
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_4,BasicForm.STATE_5,BasicForm.STATE_6,BasicForm.STATE_7,BasicForm.STATE_8,BasicForm.STATE_9,BasicForm.STATE_10,),
                'add':1,
                'change':1, 
                'delete':1, 
                'view':1,
            },
        ),
    },
    'MmAceptanceData': {
        'model': MmAceptanceData,
        'kwargs': {
            'fk_name': 'basic_form',
            'extra': 1,
        },
        'groups': (
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_5,),
                'add':1,
                'change':1, 
                'delete':1, 
                'view':1,
            },
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_1,),
                'add':1,
                'change':1, 
                'delete':0, 
                'view':0,
            },
        ),
    },
    'MOCSData': {
        'model': MOCSData,
        'kwargs': {
            'fk_name': 'basic_form',
            'extra': 1,
        },
        'groups': (
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_1,),
                'add':1,
                'change':1, 
                'delete':1, 
                'view':1,
            },
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_1,),
                'add':1,
                'change':1, 
                'delete':0, 
                'view':0,
            },
        ),
    },
    'CBSData': {
        'model': CBSData,
        'kwargs': {
            'fk_name': 'basic_form',
            'extra': 1,
        },
        'groups': (
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_1,),
                'add':1,
                'change':1, 
                'delete':1, 
                'view':1,
            },
            {
                'name': 'sswg_manager',
                'states': (BasicForm.STATE_1,),
                'add':1,
                'change':1, 
                'delete':0, 
                'view':0,
            },
        ),
    },
}

model_admin, inlines = create_main_form(main_class,inline_classes,main_mixins)

admin.site.register(model_admin.model,model_admin)
