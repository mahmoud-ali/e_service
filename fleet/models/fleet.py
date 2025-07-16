from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

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
    start_date = models.DateField(_("تاريخ البدء"))
    end_date = models.DateField(_("تاريخ الانتهاء"),blank=True,null=True)
    notes = models.TextField(_("ملاحظات"),blank=True,null=True)
    attachments = models.FileField(_("المرفقات"),blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.requested_by}({self.destination}) {self.start_date} - {self.end_date}'

    class Meta:
        verbose_name = _("المأمورية")
        verbose_name_plural = _("إدارة المأموريات")
