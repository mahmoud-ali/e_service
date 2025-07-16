from django.utils.translation import gettext_lazy as _

from .fleet import *
from .traccar import *

from django.db.models.signals import post_save
from django.dispatch import receiver

class VehicleGPSDevice(LoggingModel):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE,verbose_name=_("المركبة"))
    gps = models.OneToOneField(TcDevices, on_delete=models.CASCADE,verbose_name=_("جهاز التتبع"))

    def __str__(self) -> str:
        return f'{self.vehicle} => {self.gps.name}'

    def save(self, *args, **kwargs):
        try:
            try:
                driver = VehicleDriver.objects.filter(vehicle=self.vehicle,end_date__isnull=True).first().driver
                self.gps.phone = driver.phone
            except:
                pass

            self.gps.model = self.vehicle.model.name
            self.gps.save()
        except Exception as e:
            print("Unable to update gps device",e)


        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("جهاز تتبع مركبة")
        verbose_name_plural = _("اجهزة تتبع المركبات")

@receiver(post_save, sender=TcDevices)
def link_gps_device_with_users(sender, instance, **kwargs):
    groups = Group.objects.filter(name__in=['fleet_employee', ])
    users_emails = User.objects.filter(groups__in=groups).distinct().values_list('email', flat=True)

    with connection.cursor() as cursor:
        for tc_user in traccar.TcUsers.objects.filter(email__in=users_emails):
            cursor.execute(f"INSERT INTO tc_user_driver (userid,driverid) VALUES ({tc_user.id},{instance.id})") #,[tc_user.id,tc_driver.id]")
