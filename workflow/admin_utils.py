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

        def rerender_change_form(self,request,object_id, form_url='', extra_context=None):
            add = object_id is None
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))

            obj = self.get_object(request, unquote(object_id), to_field)
            fieldsets = self.get_fieldsets(request, obj)
            ModelForm = self.get_form(
                request, obj, change=not add, fields=flatten_fieldsets(fieldsets)
            )                
            form = ModelForm(instance=obj)
            formsets, inline_instances = self._create_formsets(
                request, obj, change=not add
            )                
            inline_formsets = self.get_inline_formsets(
                request, formsets, inline_instances, obj
            )
            readonly_fields = flatten_fieldsets(fieldsets)

            admin_form = admin.helpers.AdminForm(
                form,
                list(fieldsets),
                # Clear prepopulated fields on a view-only form to avoid a crash.
                (
                    self.get_prepopulated_fields(request, obj)
                    if add or self.has_change_permission(request, obj)
                    else {}
                ),
                readonly_fields,
                model_admin=self,
            )
            context = self.admin_site.each_context(request)
            context['original'] = obj
            context["inline_admin_formsets"] = inline_formsets
            context["adminform"] = admin_form

            self.message_user(request,_('application not confirmed!'),level=messages.ERROR)

            return self.render_change_form(
                request, context, add=add, change=not add, obj=obj, form_url=form_url
            )

        def change_view(self,request,object_id, form_url='', extra_context=None):
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            obj = self.get_object(request, unquote(object_id), to_field)

            if not obj:
                # normal save
                response = super().change_view(request,object_id, form_url, extra_context)
                return response
            
            for next_state in obj.get_next_states(request.user):
                if request.POST.get('_save_state_'+str(next_state[0]),None):
                    if obj.can_transition_to_next_state(request.user, next_state):
                        try:
                            response = super().change_view(request,object_id, form_url, extra_context)
                            obj.transition_to_next_state(request.user, next_state)
                            self.log_change(request,obj,_("Transition to")+" "+next_state[1])
                            self.message_user(request,_('application confirmed successfully!'))
                            return response
                        except:
                            return self.rerender_change_form(request,object_id, form_url, extra_context)
                    
            # normal save
            response = super().change_view(request,object_id, form_url, extra_context)
            return response
            
    return WorkflowAdminLogMixin

