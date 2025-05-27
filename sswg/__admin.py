from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.template.response import TemplateResponse
from django.contrib.admin.utils import (
    flatten_fieldsets,
    unquote,
)
from django.contrib.admin import helpers
from django.contrib.admin.options import TO_FIELD_VAR
from sswg.forms import TransferRelocationFormDataForm
from .models import BasicFormExport, COCSData, CompanyDetails, MmAceptanceData, TransferRelocationFormData, SSMOData, MOCSData, CBSData, SmrcNoObjectionData

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

class TransferRelocationFormDataInline(LogMixin,admin.TabularInline):
    model = TransferRelocationFormData
    form=TransferRelocationFormDataForm
    fk_name = 'basic_form'
    readonly_fields = ['raw_weight','allow_count']
    min_num = 1
    extra = 0

    def has_change_permission(self, request, obj=None):
        if not obj or obj.state == BasicFormExport.STATE_1:
            return True
        
        return False

    def has_add_permission(self, request, obj=None):
        if not obj or obj.state == BasicFormExport.STATE_1:
            return True
        
        return False

class CompanyDetailsInline(LogMixin,admin.StackedInline):
    model = CompanyDetails
    fk_name = 'basic_form'
    min_num = 1
    fields = ['name','surrogate_name','surrogate_id_type','surrogate_id_val','surrogate_id_phone','total_weight','total_count']
    readonly_fields = ['name','total_weight','total_count']

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == BasicFormExport.STATE_1:
            return True
        
        return False
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        
        return self.fields

class SSMODataInline(LogMixin,admin.StackedInline):
    model = SSMOData
    fk_name = 'basic_form'
    min_num = 1

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == BasicFormExport.STATE_3:
            return True
        
        return False

class SmrcNoObjectionDataInline(LogMixin,admin.StackedInline):
    model = SmrcNoObjectionData
    fk_name = 'basic_form'
    min_num = 1

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == BasicFormExport.STATE_4:
            return True
        
        return False

class MmAceptanceDataInline(LogMixin,admin.StackedInline):
    model = MmAceptanceData
    fk_name = 'basic_form'
    min_num = 1

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == BasicFormExport.STATE_5:
            return True
        
        return False

class MOCSDataInline(LogMixin,admin.StackedInline):
    model = MOCSData
    fk_name = 'basic_form'
    min_num = 1

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == BasicFormExport.STATE_7:
            return True
        
        return False

class CBSDataInline(LogMixin,admin.StackedInline):
    model = CBSData
    fk_name = 'basic_form'
    min_num = 1

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == BasicFormExport.STATE_8:
            return True
        
        return False
    
class COCDataInline(LogMixin,admin.StackedInline):
    model = COCSData
    fk_name = 'basic_form'
    min_num = 1

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == BasicFormExport.STATE_9:
            return True
        
        return False

@admin.register(BasicFormExport)
class BasicFormAdmin(LogMixin,admin.ModelAdmin):
    list_display = ('sn_no', 'date','state')
    search_fields = ('sn_no', 'date')
    list_filter = ('state',)
    exclude = ('state',)
    save_as_continue = False

    def has_change_permission(self, request, obj = None):
        if obj and obj.state == len(BasicFormExport.STATE_CHOICES):
            return False

        return super().has_change_permission(request, obj)

    def get_queryset(self, request):
        """Filter records by user's state, with full access for superusers"""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='sswg_manager').exists():
            return qs
        
        states = []
        user_groups = request.user.groups.values_list('name', flat=True)

        group_state_mapping = {
            "sswg_manager": (range(BasicFormExport.STATE_1, BasicFormExport.STATE_11)),  # All states for sswg_manager from 1-9
            "sswg_secretary": (BasicFormExport.STATE_1,BasicFormExport.STATE_11),
            "sswg_economic_security": (BasicFormExport.STATE_2,),
            "sswg_ssmo": (BasicFormExport.STATE_3,),
            "sswg_smrc": (BasicFormExport.STATE_4,),
            "sswg_mm": (BasicFormExport.STATE_5,),
            "sswg_military_intelligence": (BasicFormExport.STATE_6,),
            "sswg_moc": (BasicFormExport.STATE_7,),
            "sswg_cbs": (BasicFormExport.STATE_8,),
            "sswg_coc": (BasicFormExport.STATE_9,),
            "sswg_custom_force": (BasicFormExport.STATE_10,),
        }

        for group, state_lst in group_state_mapping.items():
            if group in user_groups:
                for state in state_lst:
                    states.append(state)

        # print("states",states)

        return qs.filter(state__in=states)

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for f in formset:
                obj = f.save(commit=False)
                if obj and hasattr(obj ,'pk'):
                    obj.updated_by = request.user
                else:
                    obj.created_by = obj.updated_by = request.user

        super().save_related(request, form, formsets, change)

    def get_readonly_fields(self, request, obj=None):
        """Make sn_no and date readonly when state progresses beyond initial state"""
        if obj and obj.state > BasicFormExport.STATE_1:
            return ('sn_no', 'date')
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.state == BasicFormExport.STATE_1:
            return True
        
        return False
    
    def get_inlines(self, request, obj):
        if request.user.is_superuser or request.user.groups.filter(name='sswg_manager').exists():
            return [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline, SmrcNoObjectionDataInline, MmAceptanceDataInline, MOCSDataInline, CBSDataInline, COCDataInline]
        
        inlines = []
        user_groups = request.user.groups.values_list('name', flat=True)

        group_inline_mapping = {
            "sswg_secretary": [TransferRelocationFormDataInline, CompanyDetailsInline, ],
            "sswg_economic_security": [TransferRelocationFormDataInline, CompanyDetailsInline, ],
            "sswg_ssmo": [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline,],
            "sswg_smrc": [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline, SmrcNoObjectionDataInline,],
            "sswg_mm": [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline, SmrcNoObjectionDataInline, MmAceptanceDataInline,],
            "sswg_military_intelligence": [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline, SmrcNoObjectionDataInline, MmAceptanceDataInline, ],
            "sswg_moc": [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline, SmrcNoObjectionDataInline, MmAceptanceDataInline, MOCSDataInline,],
            "sswg_cbs": [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline, SmrcNoObjectionDataInline, MmAceptanceDataInline, MOCSDataInline, CBSDataInline],
            "sswg_coc": [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline, SmrcNoObjectionDataInline, MmAceptanceDataInline, MOCSDataInline, CBSDataInline, COCDataInline],
            "sswg_custom_force": [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline, SmrcNoObjectionDataInline, MmAceptanceDataInline, MOCSDataInline, COCDataInline, CBSDataInline],
        }

        for group, inline_lst in group_inline_mapping.items():
            if group in user_groups:
                for inline in inline_lst:
                    inlines.append(inline)

        return list(dict.fromkeys((inlines)))
    
    def _check_data_exist(self,object_id,state):
        state_inline_mapping = {
            BasicFormExport.STATE_2: [TransferRelocationFormDataInline, ],
            BasicFormExport.STATE_4: [SSMODataInline,],
            BasicFormExport.STATE_5: [SmrcNoObjectionDataInline,],
            BasicFormExport.STATE_6: [MmAceptanceDataInline,],
            BasicFormExport.STATE_8: [MOCSDataInline,],
            BasicFormExport.STATE_9: [CBSDataInline,],
            BasicFormExport.STATE_10: [COCDataInline,],
        }

        if state_inline_mapping.get(state,None):
            for inline in state_inline_mapping[state]:
                if inline.model.objects.filter(basic_form=object_id).exists():
                    return True
        else:
            return True

        return False

    def change_view(self,request,object_id, form_url='', extra_context=None):
        add = object_id is None

        if request.POST.get('_save_confirm',None):
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))

            obj = self.get_object(request, unquote(object_id), to_field)

            if self._check_data_exist(object_id,obj.get_next_state()):
                response = super().change_view(request,object_id, form_url, extra_context)

                obj = self.get_object(request, unquote(object_id), to_field)
                obj.state = obj.get_next_state()
                obj.save()
                self.log_change(request,obj,_("SSWG State "+str(obj.state)))
                self.message_user(request,_('application confirmed successfully!'))

                return response
            else:
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

                admin_form = helpers.AdminForm(
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
        else:
            response = super().change_view(request,object_id, form_url, extra_context)
            return response