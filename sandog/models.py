from django.db import models
from django.utils.translation import gettext_lazy as _
from hr.models import EmployeeBasic, LoggingModel

class LkpSolarSystemCategory(models.Model):
    name = models.CharField(_("category name"),max_length=150)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Solar System Category")
        verbose_name_plural = _("Solar System Category")

class LkpSolarSystemPaymentMethod(models.Model):
    name = models.CharField(_("طريقة الدفع"),max_length=150)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("طريقة الدفع")
        verbose_name_plural = _("طرق الدفع")

class EmployeeSolarSystem(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    payment_method = models.ForeignKey(LkpSolarSystemPaymentMethod, on_delete=models.PROTECT,verbose_name=_("طريقة الدفع"))
    category = models.ForeignKey(LkpSolarSystemCategory, on_delete=models.PROTECT,verbose_name=_("نوع المنظومة"))

    def __str__(self) -> str:
        return f'نوع منظومة الطاقة الشمسية: {self.category.name}'

    class Meta:
        verbose_name = _("منظومة الطاقة الشمسية")
        verbose_name_plural = _("منظومة الطاقة الشمسية")
