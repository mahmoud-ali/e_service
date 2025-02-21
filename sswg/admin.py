from django.contrib import admin

from sswg.forms import TransferRelocationFormDataForm
from .models import CompanyDetails, MmAceptanceData, TransferRelocationFormData, SSMOData, BasicForm, MOCSData, CBSData, SmrcNoObjectionData

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

class TransferRelocationFormDataInline(LogMixin,admin.StackedInline):
    model = TransferRelocationFormData
    form=TransferRelocationFormDataForm
    fk_name = 'basic_form'
    readonly_fields = ['raw_weight','allow_count']
    extra = 1

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == BasicForm.STATE_1:
            return True
        
        return False

class CompanyDetailsInline(LogMixin,admin.StackedInline):
    model = CompanyDetails
    fk_name = 'basic_form'
    extra = 1
    readonly_fields = ['name','surrogate_name','surrogate_id_type','surrogate_id_val','surrogate_id_phone',]

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == BasicForm.STATE_1:
            return True
        
        return False

class SSMODataInline(LogMixin,admin.StackedInline):
    model = SSMOData
    fk_name = 'basic_form'
    extra = 1

class MOCSDataInline(LogMixin,admin.StackedInline):
    model = MOCSData
    fk_name = 'basic_form'
    extra = 1

class SmrcNoObjectionDataInline(LogMixin,admin.StackedInline):
    model = SmrcNoObjectionData
    fk_name = 'basic_form'
    extra = 1

class MmAceptanceDataInline(LogMixin,admin.StackedInline):
    model = MmAceptanceData
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
    inlines = [TransferRelocationFormDataInline, CompanyDetailsInline, SSMODataInline, SmrcNoObjectionDataInline, MmAceptanceDataInline, MOCSDataInline, CBSDataInline]

    def get_queryset(self, request):
        """Filter records by user's state, with full access for superusers"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(state=request.user.state)

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
        if obj and obj.state > BasicForm.STATE_1:
            return ('sn_no', 'date')
        return super().get_readonly_fields(request, obj)

    # def has_change_permission(self, request, obj=None):
    #     if obj and obj.state == BasicForm.STATE_1:
    #         return True
        
    #     return False
