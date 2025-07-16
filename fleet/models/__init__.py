from django.utils.translation import gettext_lazy as _

from .fleet import *
from .traccar import *

class VehicleGPSDevice(LoggingModel):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE,verbose_name=_("المركبة"))
    gps = models.OneToOneField(TcDevices, on_delete=models.SET_NULL,verbose_name=_("جهاز التتبع"),null=True,blank=True)

    def __str__(self) -> str:
        return f'{self.vehicle} => {self.gps.name}'

    class Meta:
        verbose_name = _("جهاز تتبع مركبة")
        verbose_name_plural = _("اجهزة تتبع المركبات")
