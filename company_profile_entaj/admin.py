from django.contrib import admin
from django import forms

from .models import ForeignerPermission, ForeignerPermissionType, ForeignerProcedure, ForeignerProcedureApproved, ForeignerProcedureOther, ForeignerProcedureRequirements, ForeignerRecord

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

class ForeignerPermissionInline(admin.TabularInline):
    model = ForeignerPermission
    exclude = ['state',]

@admin.register(ForeignerRecord)
class ForeignerRecordAdmin(LogAdminMixin,admin.ModelAdmin):
    inlines = [ForeignerPermissionInline]
    exclude = ['state',]
    list_display = ('company', 'name', 'position', 'department', 'salary', 'state')
    list_filter = ('state', 'company')
    search_fields = ('name', 'company__company_name_en', 'position', 'department')

@admin.register(ForeignerPermission)
class ForeignerPermissionAdmin(LogAdminMixin,admin.ModelAdmin):
    exclude = ['state',]
    list_display = ('foreigner_record', 'permission_type', 'type_id', 'validity_due_date', 'state')
    list_filter = ('permission_type', 'state')
    search_fields = ('foreigner_record__name', 'type_id')

class ForeignerProcedureApprovedInline(admin.TabularInline):
    model = ForeignerProcedureApproved

class ForeignerProcedureOtherInline(admin.TabularInline):
    model = ForeignerProcedureOther

@admin.register(ForeignerProcedure)
class ForeignerProcedureAdmin(LogAdminMixin,admin.ModelAdmin):
    exclude = ['state',]
    inlines = [ForeignerProcedureApprovedInline,ForeignerProcedureOtherInline]
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
