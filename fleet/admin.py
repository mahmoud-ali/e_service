from django.contrib import admin
from django.utils.html import format_html

from . import models


class LogMixin(admin.ModelAdmin):
    """
    A base ModelAdmin for models that inherit from LoggingModel.
    It makes the logging fields readonly and sets the user on save.
    """
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset, save it to the database, setting the
        user on each object.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            # Check if the model is an instance of LoggingModel
            # Note: models.LoggingModel is abstract, but we can check the attributes
            if hasattr(instance, 'created_by_id'):
                if not instance.pk:
                    instance.created_by = request.user
                instance.updated_by = request.user
            instance.save()
        formset.save_m2m()
        
        for obj in formset.deleted_objects:
            obj.delete()

class VehicleCertificateInline(admin.TabularInline):
    model = models.VehicleCertificate
    fields = ('cert_type','start_date','end_date','attachments','notes')
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')


class VehicleAssignmentInline(admin.TabularInline):
    model = models.VehicleAssignment
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')


class VehicleDriverInline(admin.TabularInline):
    model = models.VehicleDriver
    autocomplete_fields = ["driver"]
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

class VehicleGPSDeviceInline(admin.TabularInline):
    model = models.VehicleGPSDevice
    autocomplete_fields = ["vehicle",]
    # fields = ('cert_type','start_date','end_date','attachments','notes')
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

@admin.register(models.Vehicle)
class VehicleAdmin(LogMixin):
    list_display = ('model', 'year', 'license_plate', 'status', 'fuel_type',) #,'last_position'
    list_filter = ('status', 'fuel_type','year', 'model__make','model__name')
    search_fields = ('license_plate', 'model__name', 'model__make__name', 'year')
    inlines = [
        VehicleCertificateInline,
        VehicleAssignmentInline,
        VehicleDriverInline,
        VehicleGPSDeviceInline,
    ]

    @admin.display(description="اخر موقع")
    def last_position(self, obj):
        try:
            tc_device_pos_id = models.VehicleGPSDevice.objects.get(vehicle=obj).gps.positionid
            tc_position = models.TcPositions.objects.get(id=tc_device_pos_id)
            return format_html(f'<a target="_blank" href="https://www.google.com/maps?q={tc_position.latitude},{tc_position.longitude}">الخريطة ({tc_position.servertime})</a>')
        except Exception as e:
            # print('****',e)
            pass

        return ''

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if request.GET.get('mission_only'):
            queryset = queryset.filter(vehicleassignment__status='missions', vehicleassignment__end_date__isnull=True).distinct()
            use_distinct = True
        return queryset, use_distinct


@admin.register(models.VehicleMake)
class VehicleMakeAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(models.VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'make')
    list_filter = ('make',)
    search_fields = ('name', 'make__name')

@admin.register(models.Driver)
class DriverAdmin(LogMixin):
    list_display = ('name', 'license_no', 'license_type', 'expiry_date',)
    search_fields = ('name', 'license_no')

    list_filter = ('license_type',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        vehicle_id = request.GET.get('vehicle_id')
        if vehicle_id:
            queryset = queryset.filter(vehicledriver__vehicle_id=vehicle_id, vehicledriver__end_date__isnull=True)
        return queryset, use_distinct

@admin.register(models.VehicleAssignment)
class VehicleAssignmentAdmin(LogMixin):
    list_display = ('vehicle', 'assign_to', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'vehicle__model__make','vehicle__model','vehicle__year')
    search_fields = ('assign_to', 'vehicle__license_plate')
    autocomplete_fields = ["vehicle"]

@admin.register(models.TcDevices)
class TcDevicesAdmin(LogMixin):
    fields = ('name', 'uniqueid', )
    list_display = ('name', 'uniqueid', )
    search_fields = ('name', 'uniqueid')

    verbose_name= "قائمة اجهزة التتبع"
    

class MissionVehicleInline(admin.TabularInline):
    model = models.MissionVehicle
    fields = ('assignment',)
    #autocomplete_fields = ["assignment"]
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assignment":
            # Filter assignments for vehicles that have status 'missions'
            kwargs["queryset"] = models.VehicleDriver.objects.filter(
                vehicle__vehicleassignment__status='missions',
                vehicle__vehicleassignment__end_date__isnull=True,
                end_date__isnull=True # Only active driver assignments
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(models.Mission)
class MissionAdmin(LogMixin):
    change_form_template = 'admin/fleet/mission/change_form.html'
    fieldsets = (
        (None, {
            'fields': ('destination', 'requested_by', 'no_of_vehicles')
        }),
        ('التواريخ', {
            'fields': (('planned_start_date', 'actual_start_date'), 'no_of_days', ('planned_end_date', 'actual_end_date'))
        }),
        ('تمديد المأمورية', {
            'fields': ('is_extended', 'extension_days', ('extended_planned_end_date', 'extended_actual_end_date'))
        }),
        ('ملاحظات ومرفقات', {
            'fields': ('notes', 'attachments')
        }),
    )
    list_display = ('requested_by', 'destination', 'no_of_vehicles', 'no_of_days', 'planned_start_date', 'effective_end_display', 'actual_start_date', 'actual_end_date_display', 'status_tag')
    list_filter = ('planned_start_date', 'planned_end_date','actual_end_date','requested_by')
    search_fields = ('destination', 'requested_by', 'missionvehicle__assignment__driver__name', 'missionvehicle__assignment__vehicle__license_plate')
    readonly_fields = ('planned_end_date','actual_end_date','extended_planned_end_date','extended_actual_end_date')

    @admin.display(description="تاريخ الانتهاء")
    def effective_end_display(self, obj):
        if obj.is_extended and obj.extended_planned_end_date:
            return format_html('<b>{}</b> <span style="color:orange;">(ممدد)</span>', obj.extended_planned_end_date)
        return obj.planned_end_date

    @admin.display(description="تاريخ الانتهاء الفعلي", ordering='actual_end_date')
    def actual_end_date_display(self, obj):
        if obj.actual_end_date:
            if obj.is_extended and obj.extended_actual_end_date:
                return format_html('<b>{}</b> <span style="color:orange;">(ممدد)</span>', obj.extended_actual_end_date)
            return obj.actual_end_date
        return format_html('<span style="color: green; font-weight: bold;">جارية</span>')

    @admin.display(description="حالة الانتهاء")
    def status_tag(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        
        # 1. Determine effective start date
        start_date = obj.actual_start_date or obj.planned_start_date
        
        # 2. Determine effective end date
        if obj.is_extended:
            end_date = obj.extended_actual_end_date or obj.extended_planned_end_date
        else:
            end_date = obj.actual_end_date or obj.planned_end_date
            
        # 3. If start date is in the future, it has not started yet
        if start_date and start_date > today:
            return format_html('<span style="color: #0275d8; font-weight: bold;">لم تبدأ بعد</span>')
            
        # 4. If end date is in the past, it is completed
        if end_date and end_date < today:
            return format_html('<span style="color: #777; font-weight: bold;">منتهية</span>')
            
        # 5. Within the date range (Active / Notifications)
        if end_date:
            diff = (end_date - today).days
            if diff == 0:
                return format_html('<span style="color: white; background-color: #d9534f; padding: 3px 10px; border-radius: 10px; font-weight: bold;">تنتهي اليوم</span>')
            elif 0 < diff <= 2:
                return format_html('<span style="color: white; background-color: #f0ad4e; padding: 3px 10px; border-radius: 10px; font-weight: bold;">متبقي {} أيام</span>', diff)
        
        return format_html('<span style="color: green; font-weight: bold;">جارية</span>')

    @admin.display(description="المركبات")
    def get_vehicles(self, obj):
        vehicles = [str(mv.assignment.vehicle) for mv in obj.missionvehicle_set.all() if mv.assignment]
        if obj.vehicle: # Legacy
            vehicles.insert(0, str(obj.vehicle))
        return ", ".join(vehicles)
    # autocomplete_fields = ["vehicle","driver"]
    inlines = [MissionVehicleInline]
 
class Media:
    js = ('fleet/js/mission_extension.js',)


class VehicleMaintenancePartInline(admin.TabularInline):
    model = models.VehicleMaintenancePart
    extra = 0

@admin.register(models.VehicleMaintenance)
class VehicleMaintenanceAdmin(LogMixin):
    list_display = ('vehicle', 'service_date','next_service_due','odometer_km', 'service_type', 'service_provider','service_total_cost')
    list_filter = ('vehicle__model__make','vehicle__model','vehicle__year','service_date', 'service_type','service_provider')
    search_fields = ('vehicle__license_plate',)
    autocomplete_fields = ["vehicle",]
    inlines = [
        VehicleMaintenancePartInline,
    ]



# @admin.register(models.VehicleCertificate)
# class VehicleCertificateAdmin(LogMixin):
#     list_display = ('vehicle', 'cert_type', 'start_date', 'end_date')
#     list_filter = ('cert_type', 'vehicle')
#     search_fields = ('vehicle__license_plate',)

@admin.register(models.VehicleDriver)
class VehicleDriverAdmin(LogMixin):
    list_display = ('vehicle', 'driver', 'start_date', 'end_date')
    search_fields = ('vehicle__license_plate', 'driver__name', 'vehicle__model__name')

# Register simple models without customization
# admin.site.register(models.VehicleFuelType)
# admin.site.register(models.VehicleStatus)
admin.site.register(models.DriverLicenseType)
admin.site.register(models.VehicleCertificateType)
# admin.site.register(models.ServiceType)
admin.site.register(models.ServiceProvider)
# admin.site.register(models.VehicleSparePart)

@admin.register(models.ServiceType)
class ServiceTypeAdmin(LogMixin):
    fieldsets = (
        (None, {
            "fields": (
                'name',
            ),
        }),
        ('الخدمة او الصيانة الدزرية', {
            "fields": (
                'periodic','no_of_days',
            ),
        }),
    )
    list_display = ('name', 'periodic','no_of_days',)
    list_filter = ('periodic',)
    search_fields = ('name',)
