from django.db import models
from django.utils.translation import gettext_lazy as _
from hr.models import EmployeeBasic, LoggingModel

class LkpSolarSystemCategory(LoggingModel):
    name = models.CharField(_("category name"),max_length=150)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Solar System Category")
        verbose_name_plural = _("Solar System Category")

class EmployeeSolarSystem(LoggingModel):
    employee = models.OneToOneField(EmployeeBasic, related_name="solar_system_category_choice", on_delete=models.PROTECT,verbose_name=_("employee_name"))
    category = models.ForeignKey(LkpSolarSystemCategory, on_delete=models.PROTECT,verbose_name=_("المجموعة"))

    def __str__(self) -> str:
        return f'نوع منظومة الطاقة الشمسية: {self.get_category_display()}'

    class Meta:
        verbose_name = _("منظومة الطاقة الشمسية")
        verbose_name_plural = _("منظومة الطاقة الشمسية")
