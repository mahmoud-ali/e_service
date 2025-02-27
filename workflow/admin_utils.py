from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.admin.utils import (
    flatten_fieldsets,
    unquote,
)
from django.contrib.admin.options import TO_FIELD_VAR

def create_main_form(main_class,inline_classes,global_mixins):
    inlines = {}
    for model_name, inline_attrs in inline_classes.items():
        inline_types = [admin.StackedInline, admin.TabularInline, ]

        model_mixin = list(set(inline_attrs.get('mixins', [])))

        for t in inline_types:
            if t in model_mixin:
                break
        else:
            model_mixin.append(inline_types[0])
            
        cls_dict = {
            'model': inline_attrs['model'],
        }

        for attr, value in inline_attrs.get('kwargs',{}).items():
            cls_dict[attr] = value
            
        inline_class = type(
            f'{model_name}Inline',
            tuple(model_mixin),
            cls_dict,
        )
        inlines[model_name] = inline_class

    workflow_mixin = get_workflow_mixin(main_class,inline_classes,inlines)
    model_mixin = main_class.get('mixins', []) + [workflow_mixin] + global_mixins

    if not admin.ModelAdmin in model_mixin:
        model_mixin.append(admin.ModelAdmin)
        
    cls_dict = {
        'model': main_class['model'],
    }

    for attr, value in main_class.get('kwargs',{}).items():
        cls_dict[attr] = value

    
        
    model_admin =  type(
        f'{main_class.get("model").__name__}',
        tuple(model_mixin),
        cls_dict,
    )

    return (model_admin, inlines)

def view_model_states(inline_val={},user_groups=[]):
    """Check if the user can view the model based on their group permissions"""
    view_states = set()
    for group_dict in inline_val.get("groups"):
        group = group_dict.get("name",'')
        if group in user_groups:
            states = group_dict.get("states",set())
            view_states.update(states)

    return view_states
    
def get_workflow_mixin(main_class,inline_classes={},inlines_dict={}):
    class WorkflowAdminLogMixin():
        def get_queryset(self, request):
            """Filter records by user's state, with full access for superusers"""
            qs = super().get_queryset(request)
            user_groups = list(request.user.groups.values_list('name', flat=True))

            states = view_model_states(main_class,user_groups)

            return qs.filter(state__in=states)
        
        def get_inlines(self, request, obj):        
            inlines = []
            user_groups = list(request.user.groups.values_list('name', flat=True))

            states = set()
            for model_name, inline_attrs in inline_classes.items():
                states = view_model_states(inline_attrs,user_groups)

                if obj and (obj.state in states):
                    inlines.append(inlines_dict[model_name])

            return inlines

    return WorkflowAdminLogMixin