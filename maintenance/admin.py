from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from maintenance.models import (
    MaintenanceUnit, FaultCategory, MaintenanceRequest,
    CompletionReport, ServiceRating, SparePart, StockMovement,
    LowStockAlert, Notification
)


@admin.register(MaintenanceUnit)
class MaintenanceUnitAdmin(admin.ModelAdmin):
    list_display   = ['code', 'name', 'group_name', 'icon', 'requires_safety_permit']
    list_filter    = ['requires_safety_permit']
    list_editable  = ['requires_safety_permit']
    search_fields  = ['code', 'name']


class FaultCategoryInline(admin.TabularInline):
    model      = FaultCategory
    extra      = 0
    fields     = ['sub_category', 'name', 'order', 'is_active', 'requires_safety_permit']


@admin.register(FaultCategory)
class FaultCategoryAdmin(admin.ModelAdmin):
    list_display   = ['unit', 'sub_category', 'name', 'order', 'is_active', 'requires_safety_permit']
    list_filter    = ['unit', 'is_active', 'requires_safety_permit']
    search_fields  = ['name', 'sub_category']
    list_editable  = ['order', 'is_active', 'requires_safety_permit']
    ordering       = ['unit', 'order', 'name']


class CompletionReportInline(admin.StackedInline):
    model  = CompletionReport
    extra  = 0
    fields = ['technician', 'work_done', 'root_cause', 'recommendations']


class ServiceRatingInline(admin.TabularInline):
    model      = ServiceRating
    extra      = 0
    fields     = ['rating', 'comment']
    readonly_fields = ['rating', 'comment']


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display   = ['request_number', 'employee_name', 'general_dept', 'department',
                      'fault_category', 'assigned_unit', 'status', 'priority', 'created_at']
    list_filter    = ['status', 'priority', 'assigned_unit', 'fault_category__unit']
    search_fields  = ['request_number', 'employee_name', 'department', 'general_dept']
    readonly_fields = ['request_number', 'created_at', 'updated_at', 'assigned_unit']
    ordering       = ['-created_at']
    inlines        = [CompletionReportInline, ServiceRatingInline]
    fieldsets      = (
        (_('بيانات الطلب'), {
            'fields': ('request_number', 'requester', 'employee_name', 'general_dept', 'department', 'location')
        }),
        (_('تفاصيل العطل'), {
            'fields': ('fault_category', 'fault_description', 'priority')
        }),
        (_('التعيين والحالة'), {
            'fields': ('assigned_unit', 'assigned_technician', 'status', 'admin_notes')
        }),
        (_('التواريخ'), {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display  = ['sku', 'name', 'unit', 'quantity_in_stock', 'reorder_point',
                     'unit_of_measure', 'is_active', 'is_low_stock_display']
    list_filter   = ['unit', 'is_active']
    search_fields = ['sku', 'name']
    list_editable = ['reorder_point', 'is_active']

    @admin.display(description=_('مخزون منخفض؟'), boolean=True)
    def is_low_stock_display(self, obj):
        return obj.is_low_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display  = ['spare_part', 'movement_type', 'quantity', 'maintenance_request',
                     'performed_by', 'created_at']
    list_filter   = ['movement_type', 'spare_part__unit']
    search_fields = ['spare_part__name', 'spare_part__sku']
    readonly_fields = ['created_at']


@admin.register(LowStockAlert)
class LowStockAlertAdmin(admin.ModelAdmin):
    list_display  = ['spare_part', 'quantity_at_alert', 'is_resolved', 'created_at']
    list_filter   = ['is_resolved']
    search_fields = ['spare_part__name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter   = ['notification_type', 'is_read']
    search_fields = ['recipient__email', 'title']
