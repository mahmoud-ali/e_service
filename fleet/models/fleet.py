from datetime import timedelta
from django.db import models
from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import connection

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

import fleet.models.traccar as traccar

User = get_user_model()

class LoggingModel(models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

#Vehicle Information  
class VehicleMake(models.Model):
    name = models.CharField(_("الاسم"),max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("الشركة المصنعة")
        verbose_name_plural = _("قائمة الشركات المصنعة")

class VehicleModel(models.Model):
    make = models.ForeignKey(VehicleMake, on_delete=models.PROTECT,verbose_name=_("الشركة المصنعة"))
    name = models.CharField(_("الاسم"),max_length=100)

    def __str__(self) -> str:
        return f'{self.make.name} - {self.name}'

    class Meta:
        verbose_name = _("موديل المركبة")
        verbose_name_plural = _("قائمة موديلات المركبات")

class VehicleFuelType(models.Model):
    name = models.CharField(_("الاسم"),max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("نوع الوقود")
        verbose_name_plural = _("قائمة انواع الوقود")

class VehicleStatus(models.Model):
    name = models.CharField(_("الاسم"),max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("حالة المركبة")
        verbose_name_plural = _("قائمة حالات المركبات")

class Vehicle(LoggingModel):
    model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT,verbose_name=_("نوع العربة"))
    year = models.IntegerField(_("سنة الصنع"))
    fuel_type = models.ForeignKey(VehicleFuelType, on_delete=models.PROTECT,verbose_name=_("نوع الوقود"))
    license_plate = models.CharField(_("رقم اللوحة"),max_length=100,unique=True)
    machine_number = models.CharField(_("رقم المكنة"),max_length=100,blank=True,null=True)
    chassis_number = models.CharField(_("رقم الشاسي"),max_length=100,blank=True,null=True)
    book_value = models.CharField(_("القيمة التقديرية"),max_length=100,default=0)
    status = models.ForeignKey(VehicleStatus, on_delete=models.PROTECT,verbose_name=_("الحالة"))

    def __str__(self) -> str:
        return f'{self.model.name} - {self.year}({self.license_plate})'

    class Meta:
        verbose_name = _("المركبة")
        verbose_name_plural = _("إدارة المركبات")

#Drivers info
class DriverLicenseType(models.Model):
    name = models.CharField(_("الاسم"),max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("نوع الرخصة")
        verbose_name_plural = _("قائمة انواع الرخص")

class Driver(LoggingModel):
    name = models.CharField(_("الاسم"),max_length=100)
    license_no = models.CharField(_("رقم الرخصة"),max_length=100)
    license_type = models.ForeignKey(DriverLicenseType, on_delete=models.PROTECT,verbose_name=_("نوع الرخصة"))
    expiry_date = models.DateField(_("تاريخ انتهاء الرخصة"))
    phone = models.CharField(_("رقم الهاتف"),max_length=100)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not traccar.TcDrivers.objects.filter(uniqueid=self.license_no).exists():
            tc_driver = traccar.TcDrivers.objects.create(name=self.name,uniqueid=self.license_no,attributes=f'{{"phone":"{self.phone}"}}')

            groups = Group.objects.filter(name__in=['fleet_employee', ])
            users_emails = User.objects.filter(groups__in=groups).distinct().values_list('email', flat=True)

            with connection.cursor() as cursor:
                for tc_user in traccar.TcUsers.objects.filter(email__in=users_emails):
                    cursor.execute(f"INSERT INTO tc_user_driver (userid,driverid) VALUES ({tc_user.id},{tc_driver.id})") #,[tc_user.id,tc_driver.id]")

            #traccar.TcUserDriver.objects.create(userid=tc_user,driverid=tc_driver)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("السائق")
        verbose_name_plural = _("قائمة السائقين")

class VehicleDriver(LoggingModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT,verbose_name=_("المركبة"))
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT,verbose_name=_("السائق"))
    start_date = models.DateField(_("تاريخ البدء"))
    end_date = models.DateField(_("تاريخ الانتهاء"),blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.vehicle.model.name}({self.vehicle.license_plate}) - {self.driver.name}'

    class Meta:
        verbose_name = _("سائق مركبة")
        verbose_name_plural = _("سائقي المركبات")

class VehicleAssignment(LoggingModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT,verbose_name=_("المركبة"))
    assign_to = models.CharField(_("اسم الموظف او الجهة المخصص لها"),max_length=100)
    start_date = models.DateField(_("تاريخ البدء"))
    end_date = models.DateField(_("تاريخ الانتهاء"),blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.vehicle.model.name}({self.vehicle.license_plate}) - {self.assign_to}'

    class Meta:
        verbose_name = _("تخصيص مركبة")
        verbose_name_plural = _("إدارة تخصيص المركبات")

#License management
class VehicleCertificateType(models.Model):
    name = models.CharField(_("الاسم"),max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("نوع شهادة مركبة")
        verbose_name_plural = _("قائمة انواع شهادات المركبات")

class VehicleCertificate(LoggingModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT,verbose_name=_("المركبة"))
    cert_type = models.ForeignKey(VehicleCertificateType, on_delete=models.PROTECT,verbose_name=_("نوع الشهادة"))
    start_date = models.DateField(_("تاريخ البداية"))
    end_date = models.DateField(_("تاريخ تاريخ النهاية"))
    notes = models.TextField(_("ملاحظات"),blank=True,null=True)
    attachments = models.FileField(_("المرفقات"),blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.vehicle.model.name} ({self.vehicle.license_plate}) - {self.cert_type.name} {self.end_date}'

    class Meta:
        verbose_name = _("شهادة المركبة")
        verbose_name_plural = _("قائمة شهادات المركبات")

#Maintenance
# class VehicleMaintenance(LoggingModel):
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT,verbose_name=_("المركبة"))
#     service_date = models.DateField(_("تاريخ الصيانة"))
#     service_type = models.CharField(_("نوع الصيانة"),max_length=100)
#     service_provider = models.CharField(_("مقدم الصيانة"),max_length=100)
#     cost = models.FloatField(_("التكلفة"))
#     next_due = models.DateField(_("تاريخ الاستحقاق التالي"),blank=True,null=True)
#     notes = models.TextField(_("ملاحظات"),blank=True,null=True)

#     def __str__(self) -> str:
#         return f'{self.vehicle.model.name} ({self.vehicle.license_plate}) - {self.service_type}'

#     class Meta:
#         verbose_name = _("صيانة المركبة")
#         verbose_name_plural = _("صيانة المركبات")

# #
# class VehicleOdometer(LoggingModel):
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT,verbose_name=_("المركبة"))
#     date = models.DateField(_("التاريخ"))
#     odometer = models.FloatField(_("قراءة عداد المسافة"))

#     def __str__(self) -> str:
#         return f'{self.vehicle.model.name} ({self.vehicle.license_plate}) - {self.date}: {self.odometer}'

#     class Meta:
#         verbose_name = _("عداد المسافة")
#         verbose_name_plural = _("عداد المسافة")

class Mission(LoggingModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT,verbose_name=_("المركبة"))
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT,verbose_name=_("السائق"))
    destination = models.CharField(_("الوجهة"),max_length=100)
    requested_by = models.CharField(_("الجهة الطالبة"),max_length=100)
    planned_start_date = models.DateField(_("تاريخ البدء المخطط"))
    actual_start_date = models.DateField(_("تاريخ البدء الفعلي"),blank=True,null=True)
    no_of_days = models.IntegerField(_("عدد الأيام"),)
    planned_end_date = models.DateField(_("تاريخ الانتهاء المخطط"),blank=True,null=True,editable=False)
    actual_end_date = models.DateField(_("تاريخ الانتهاء الفعلي"),blank=True,null=True,editable=False)
    notes = models.TextField(_("ملاحظات"),blank=True,null=True)
    attachments = models.FileField(_("المرفقات"),blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.requested_by}({self.destination}) {self.planned_start_date} - {self.no_of_days}'
    
    def save(self, *args, **kwargs):
        self.planned_end_date = self.planned_start_date + timedelta(days=self.no_of_days)
        if self.actual_start_date:
            self.actual_end_date = self.actual_start_date + timedelta(days=self.no_of_days)
        else:
            self.actual_end_date = None
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = _("المأمورية")
        verbose_name_plural = _("إدارة المأموريات")


#maintenance
class ServiceType(models.Model):
    name = models.CharField(_("الاسم"),max_length=100)
    periodic = models.BooleanField(_("خدمة دورية؟"),default=False)
    no_of_days = models.IntegerField(_("عدد الأيام"),blank=True,null=True)


    def __str__(self) -> str:
        return self.name
    
    def clean(self):
        if self.periodic and self.no_of_days is None:
            raise ValidationError(
                    {"no_of_days":_("حدد عدد الأيام للصيانة/الخدمة القادمة")}
                ) 
        
        return super().clean()

    class Meta:
        verbose_name = _("نوع الصيانة")
        verbose_name_plural = _("قائمة انواع الصيانة")

class ServiceProvider(models.Model):
    name = models.CharField(_("الاسم"),max_length=100)
    phone = models.CharField(_("رقم الهاتف"),max_length=100)
    address = models.TextField(_("العنوان"))
    notes = models.TextField(_("ملاحظات"),blank=True,null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("مقدم الخدمة")
        verbose_name_plural = _("قائمة مقدمي الخدمات")

class VehicleMaintenance(LoggingModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT,verbose_name=_("المركبة"))
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT,verbose_name=_("نوع الصيانة"))
    service_date = models.DateField(_("تاريخ الصيانة"))
    next_service_due = models.DateField(_("تاريخ الصيانة التالية"),help_text=_("في حال الصيانة/الخدمة الدورية"),blank=True,null=True,editable=False)
    odometer_km = models.FloatField(_("قراءة عداد المسافة (كم)"))
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.PROTECT,verbose_name=_("مقدم الخدمة"))
    service_total_cost = models.DecimalField(_("التكلفة الكلية (جنيه)"),max_digits=10, decimal_places=2)
    downtime_hrs = models.FloatField(_("وقت التوقف (ساعات)"),blank=True,null=True)
    notes = models.TextField(_("ملاحظات"),blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.vehicle.license_plate} - {self.service_type.name} on {self.service_date}'

    def save(self, *args, **kwargs):
        if self.service_type.periodic:
            self.next_service_due = self.service_date + timedelta(days=self.service_type.no_of_days)
        else:
            self.next_service_due = None

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("صيانة المركبة")
        verbose_name_plural = _("إدارة صيانة المركبات")

# class VehicleSparePart(models.Model):
#     name = models.CharField(_("الاسم"),max_length=100)

#     def __str__(self) -> str:
#         return self.name
    
#     class Meta:
#         verbose_name = _("اسبير مركبة")
#         verbose_name_plural = _("اسبيرات المركبات")

class VehicleMaintenancePart(models.Model):
    maintenance = models.ForeignKey(VehicleMaintenance, on_delete=models.PROTECT,verbose_name=_("صيانة"))
    part = models.CharField(_("الاسبير"),max_length=100)
    quantity = models.IntegerField(_("الكمية"))
    unit_price = models.DecimalField(_("سعر الوحدة (جنيه)"),max_digits=10, decimal_places=2)
    notes = models.TextField(_("ملاحظات"),blank=True,null=True)

    def __str__(self):
        return f'{self.maintenance.vehicle.license_plate} - {self.part}'
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    
    class Meta:
        verbose_name = _("اسبير مركبة")
        verbose_name_plural = _("اسبيرات المركبات")