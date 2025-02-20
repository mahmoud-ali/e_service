from django.contrib import admin

from sswg.forms import SMRCDataForm
from .models import CompanyDetails, SMRCData, SSMOData, BasicForm, MOCSData, CBSData

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

class SMRCDataInline(LogMixin,admin.StackedInline):
    model = SMRCData
    form=SMRCDataForm
    fk_name = 'basic_form'
    readonly_fields = ['raw_weight','allow_count']
    extra = 1

class CompanyDetailsInline(LogMixin,admin.StackedInline):
    model = CompanyDetails
    fk_name = 'basic_form'
    extra = 1
    readonly_fields = ['name','surrogate_name','surrogate_id_type','surrogate_id_val','surrogate_id_phone',]

class SSMODataInline(LogMixin,admin.StackedInline):
    model = SSMOData
    fk_name = 'basic_form'
    extra = 1

class MOCSDataInline(LogMixin,admin.StackedInline):
    model = MOCSData
    fk_name = 'basic_form'
    extra = 1

class CBSDataInline(LogMixin,admin.StackedInline):
    model = CBSData
    fk_name = 'basic_form'
    extra = 1

@admin.register(BasicForm)
class BasicFormAdmin(LogMixin,admin.ModelAdmin):
    list_display = ('sn_no', 'date')
    search_fields = ('sn_no', 'date')
    inlines = [SMRCDataInline, CompanyDetailsInline, SSMODataInline, MOCSDataInline, CBSDataInline]

    def save_related(self,request, form, formsets, change):
        for formset in formsets:
            for f in formset:
                obj = f.save(commit=False)
                if obj and hasattr(obj ,'pk'):
                    obj.updated_by = request.user
                else:
                    obj.created_by = obj.updated_by = request.user

        super().save_related(request, form, formsets, change)

@admin.register(CompanyDetails)
class CompanyDetailsAdmin(LogMixin,admin.ModelAdmin):
    list_display = ('name', 'surrogate_name', 'surrogate_id_type')
    search_fields = ('name', 'surrogate_name')
    list_filter = ('surrogate_id_type',)

@admin.register(SMRCData)
class SMRCDataAdmin(LogMixin,admin.ModelAdmin):
    form=SMRCDataForm
    list_display = ('raw_weight', 'allow_count')
    search_fields = ('raw_weight', 'allow_count')

@admin.register(SSMOData)
class SSMODataAdmin(LogMixin,admin.ModelAdmin):
    list_display = ('certificate_id', 'raw_weight', 'net_weight', 'allow_count')
    search_fields = ('certificate_id',)
    list_filter = ('allow_count',)
