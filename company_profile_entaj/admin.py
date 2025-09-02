from django.contrib import admin
from django import forms

from workflow.admin_utils import create_main_form

from .models import ForeignerPermission, ForeignerPermissionType, ForeignerProcedure, ForeignerProcedurePermanent, ForeignerProcedureVisitor, ForeignerProcedureRequirements, ForeignerRecord

class LogAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
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

# class ForeignerPermissionInline(admin.TabularInline):
#     model = ForeignerPermission
#     exclude = ['state',]

# @admin.register(ForeignerRecord)
# class ForeignerRecordAdmin(LogAdminMixin,admin.ModelAdmin):
#     inlines = [ForeignerPermissionInline]
#     exclude = ['state',]
#     list_display = ('company', 'name', 'position', 'department', 'salary', 'state')
#     list_filter = ('state', 'company')
#     search_fields = ('name', 'company__company_name_en', 'position', 'department')

# @admin.register(ForeignerPermission)
# class ForeignerPermissionAdmin(LogAdminMixin,admin.ModelAdmin):
#     exclude = ['state',]
#     list_display = ('foreigner_record', 'permission_type', 'type_id', 'validity_due_date', 'state')
#     list_filter = ('permission_type', 'state')
#     search_fields = ('foreigner_record__name', 'type_id')

class ForeignerProcedurePermanentInline(admin.TabularInline):
    model = ForeignerProcedurePermanent

class ForeignerProcedureVisitorInline(admin.TabularInline):
    model = ForeignerProcedureVisitor

@admin.register(ForeignerProcedure)
class ForeignerProcedureAdmin(LogAdminMixin,admin.ModelAdmin):
    exclude = ['state',]
    inlines = [ForeignerProcedurePermanentInline,ForeignerProcedureVisitorInline]
    list_display = ('company', 'procedure_type', 'procedure_from', 'procedure_to', 'state')
    list_filter = ('procedure_type', 'state')
    search_fields = ('company__company_name_en', 'procedure_type__name')

class ForeignerProcedureRequirementsAdminForm(forms.ModelForm):
    class Meta:
        model = ForeignerProcedureRequirements
        fields = '__all__'
        widgets = {
            'cert_type': forms.CheckboxSelectMultiple,
            'parent_procedure_type': forms.CheckboxSelectMultiple,
        }
        
@admin.register(ForeignerProcedureRequirements)
class ForeignerProcedureRequirementsAdmin(admin.ModelAdmin):
    form = ForeignerProcedureRequirementsAdminForm
    list_display = ('child_procedure_type',)

@admin.register(ForeignerPermissionType)
class ForeignerPermissionTypeAdmin(admin.ModelAdmin):
    list_display = ('name','minimum_no_months',)

######################## Foreigner Record ############################

foreigner_record_main_mixins = [LogAdminMixin]
foreigner_record_main_class = {
    'model': ForeignerRecord,
    'mixins': [],
    # 'static_inlines': [],
    'kwargs': {
        'list_display': ('company', 'name', 'position', 'department', 'salary', 'state'),
        'list_filter': ('state', 'employment_type', 'position', 'department'),
        'search_fields': ('name', 'company__company_name_en', 'position', 'department'),
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': {
        'entaj_section_head':{
            'permissions': {
                ForeignerRecord.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # ForeignerRecord.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # ForeignerRecord.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'entaj_department_head':{
            'permissions': {
                # ForeignerRecord.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                ForeignerRecord.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                ForeignerRecord.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        # 'entaj_gm':{
        #     'permissions': {
        #         ForeignerRecord.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
        #         ForeignerRecord.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
        #         ForeignerRecord.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
        #     },
        # },

    },
}

foreigner_record_inline_classes = {
    'ForeignerPermission': {
        'model': ForeignerPermission,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 0,
            'min_num': 1,
            'exclude': ['state',]
        },
        'groups': {
            'entaj_section_head':{
                'permissions': {
                ForeignerRecord.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # ForeignerRecord.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # ForeignerRecord.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'entaj_department_head':{
                'permissions': {
                # ForeignerRecord.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                ForeignerRecord.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                ForeignerRecord.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            # 'entaj_gm':{
            #     'permissions': {
            #     ForeignerRecord.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
            #     ForeignerRecord.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            #     ForeignerRecord.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            #     },
            # },
        },
    },
}

foreigner_record_admin, inlines = create_main_form(foreigner_record_main_class,foreigner_record_inline_classes,foreigner_record_main_mixins)

admin.site.register(foreigner_record_admin.model,foreigner_record_admin)

######################## Foreigner Permissions ############################
foreigner_permission_main_mixins = [LogAdminMixin]
foreigner_permission_main_class = {
    'model': ForeignerPermission,
    'mixins': [],
    # 'static_inlines': [],
    'kwargs': {
        'list_display': ('foreigner_record', 'permission_type', 'type_id', 'validity_due_date', 'state'),
        'list_filter': ('permission_type', 'state','validity_due_date',),
        'search_fields': ('foreigner_record__name', 'type_id'),
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': {
        'entaj_section_head':{
            'permissions': {
                ForeignerPermission.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                # ForeignerPermission.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                # ForeignerPermission.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'entaj_department_head':{
            'permissions': {
                # ForeignerPermission.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                ForeignerPermission.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                ForeignerPermission.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        # 'entaj_gm':{
        #     'permissions': {
        #         ForeignerPermission.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
        #         ForeignerPermission.STATE_CONFIRMED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
        #         ForeignerPermission.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
        #     },
        # },

    },
}

foreigner_permission_inline_classes = {}

foreigner_permission_admin, inlines = create_main_form(foreigner_permission_main_class,foreigner_permission_inline_classes,foreigner_permission_main_mixins)

admin.site.register(foreigner_permission_admin.model,foreigner_permission_admin)
