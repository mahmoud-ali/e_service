from django.utils.translation import gettext_lazy as _

from .fleet import *
from .traccar import *

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
