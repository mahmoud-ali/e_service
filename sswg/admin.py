from django.contrib import admin
from .models import CompanyDetails, SMRCData, SSMOData, BasicForm, MOCSData, CBSData

class SMRCDataInline(admin.StackedInline):
    model = SMRCData
    fk_name = 'basic_form'
    extra = 1

class CompanyDetailsInline(admin.StackedInline):
    model = CompanyDetails
    fk_name = 'basic_form'
    extra = 1

class SSMODataInline(admin.StackedInline):
    model = SSMOData
    fk_name = 'basic_form'
    extra = 1

class MOCSDataInline(admin.StackedInline):
    model = MOCSData
    fk_name = 'basic_form'
    extra = 1

class CBSDataInline(admin.StackedInline):
    model = CBSData
    fk_name = 'basic_form'
    extra = 1

@admin.register(BasicForm)
class BasicFormAdmin(admin.ModelAdmin):
    list_display = ('sn_no', 'date')
    search_fields = ('sn_no', 'date')
    inlines = [SMRCDataInline, CompanyDetailsInline, SSMODataInline, MOCSDataInline, CBSDataInline]

@admin.register(CompanyDetails)
class CompanyDetailsAdmin(admin.ModelAdmin):
    list_display = ('name', 'surrogate_name', 'surrogate_id_type')
    search_fields = ('name', 'surrogate_name')
    list_filter = ('surrogate_id_type',)

@admin.register(SMRCData)
class SMRCDataAdmin(admin.ModelAdmin):
    list_display = ('raw_weight', 'allow_count')
    search_fields = ('raw_weight', 'allow_count')

@admin.register(SSMOData)
class SSMODataAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'raw_weight', 'net_weight', 'allow_count')
    search_fields = ('certificate_id',)
    list_filter = ('allow_count',)
