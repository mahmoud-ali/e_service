from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from mokhalafat.forms import AppMokhalafatAdminForm, AppChemicalMaterialsViolationForm
from mokhalafat.models import (
    AppMokhalafat, 
    AppMokhalafatProcedure, 
    AppMokhalafatRecommendation,
    AppChemicalMaterialsViolation,
    AppChemicalMaterialsViolationItem,
    AppChemicalMaterialsViolationWitness,
    AppChemicalMaterialsViolationAttachment
)

class LogAdminMixin:
    def has_add_permission(self, request):
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request,obj)

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request,obj)

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class AppMokhalafatProcedureInline(admin.TabularInline):
    model = AppMokhalafatProcedure
    extra = 1    

class AppMokhalafatRecommendationInline(admin.TabularInline):
    model = AppMokhalafatRecommendation
    extra = 1    

class AppMokhalafatAdmin(LogAdminMixin,admin.ModelAdmin):
    # model = AppMokhalafat
    form = AppMokhalafatAdminForm
    inlines = [AppMokhalafatProcedureInline,AppMokhalafatRecommendationInline]
    fields = ["code","date","aism_almukhalafa","wasf_almukhalafa","tahlil_almukhalafa"]
    list_display = ["date","code","aism_almukhalafa","tahlil_almukhalafa"]
    list_filter = ["date"]
    search_fields = ["code","aism_almukhalafa","wasf_almukhalafa","tahlil_almukhalafa"]
    view_on_site = False

admin.site.register(AppMokhalafat, AppMokhalafatAdmin)


class AppChemicalMaterialsViolationItemInline(admin.TabularInline):
    model = AppChemicalMaterialsViolationItem
    extra = 1


class AppChemicalMaterialsViolationWitnessInline(admin.TabularInline):
    model = AppChemicalMaterialsViolationWitness
    extra = 1


class AppChemicalMaterialsViolationAttachmentInline(admin.TabularInline):
    model = AppChemicalMaterialsViolationAttachment
    extra = 1


class AppChemicalMaterialsViolationAdmin(LogAdminMixin, admin.ModelAdmin):
    form = AppChemicalMaterialsViolationForm
    inlines = [
        AppChemicalMaterialsViolationItemInline, 
        AppChemicalMaterialsViolationWitnessInline,
        AppChemicalMaterialsViolationAttachmentInline
    ]
    list_display = ["date", "time", "state", "officer_name", "incident_type"]
    list_filter = ["date", "state", "incident_type", "public_health_risk"]
    search_fields = ["officer_name", "city_or_village", "neighborhood", "location_details", "owner_statements"]
    view_on_site = False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields = list(readonly_fields) + ['state']
        return readonly_fields

    fieldsets = (
        (_("معلومات الضبط الأساسية والمكان"), {
            'fields': ('date', 'time', 'state', 'city_or_village', 'neighborhood', 'house', 'location_details')
        }),
        (_("بيانات القائم بالضبط"), {
            'fields': ('officer_name', 'officer_job', 'officer_org')
        }),
        (_("تفاصيل الواقعة"), {
            'fields': ('incident_type',)
        }),
        (_("حالة التخزين"), {
            'fields': ('is_safely_stored', 'ventilation', 'has_warning_labels', 'near_heat_or_flame')
        }),
        (_("تقييم المخاطر"), {
            'fields': ('public_health_risk', 'fire_explosion_risk', 'environmental_risk')
        }),
        (_("إجراءات أولية يجب اتباعها"), {
            'fields': (
                'proc_secure_site', 
                'proc_notify_authorities', 
                'proc_prevent_handling', 
                'proc_notify_violations', 
                'proc_educate_owner'
            )
        }),
        (_("أقوال صاحب الموقع"), {
            'fields': ('owner_statements',)
        }),
        (_("التوقيعات"), {
            'fields': ('officer_signature_name', 'owner_signature_name')
        }),
    )

admin.site.register(AppChemicalMaterialsViolation, AppChemicalMaterialsViolationAdmin)


