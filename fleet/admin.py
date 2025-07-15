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
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

class VehicleGPSDeviceInline(admin.TabularInline):
    model = models.VehicleGPSDevice
    # fields = ('cert_type','start_date','end_date','attachments','notes')
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

@admin.register(models.Vehicle)
class VehicleAdmin(LogMixin):
    list_display = ('model', 'year', 'license_plate', 'status', 'fuel_type','last_position',)
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
            print("pos_id",tc_device_pos_id)
            tc_position = models.TcPositions.objects.get(id=tc_device_pos_id)
            return format_html(f'<a href="https://www.google.com/maps?q={tc_position.latitude},{tc_position.longitude}">عرض الخريطة</a>')
        except Exception as e:
            # print('****',e)
            pass

        return format_html(f'<a href="https://www.google.com/maps?q=X,Y">عرض الخريطة</a>')

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset, save it to the database, setting the
        user on each object.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()


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

@admin.register(models.VehicleAssignment)
class VehicleAssignmentAdmin(LogMixin):
    list_display = ('vehicle', 'assign_to', 'start_date', 'end_date')
    list_filter = ('vehicle__model__make','vehicle__model','vehicle__year')
    search_fields = ('assign_to', 'vehicle__license_plate')
    autocomplete_fields = ["vehicle"]

# @admin.register(models.VehicleCertificate)
# class VehicleCertificateAdmin(LogMixin):
#     list_display = ('vehicle', 'cert_type', 'start_date', 'end_date')
#     list_filter = ('cert_type', 'vehicle')
#     search_fields = ('vehicle__license_plate',)

# @admin.register(models.VehicleDriver)
# class VehicleDriverAdmin(LogMixin):
#     list_display = ('vehicle', 'driver', 'start_date', 'end_date')
#     # list_filter = ('vehicle', 'driver')
#     search_fields = ('vehicle__license_plate', 'driver__name')

# Register simple models without customization
# admin.site.register(models.VehicleFuelType)
# admin.site.register(models.VehicleStatus)
admin.site.register(models.DriverLicenseType)
# admin.site.register(models.VehicleCertificateType)