from django.db import models
from django.utils.translation import gettext_lazy as _
from hr.models import EmployeeBasic, LoggingModel

class EmployeeSolarSystem(LoggingModel):
    CAT1 = 1
    CAT2 = 2
    CAT3 = 3

    CAT_CHOICES = {
        CAT1: _('المجموعة الاولى'),
        CAT2: _('المجموعة الثانية'),
        CAT3: _('المجموعة الثالثة'),
    }

    employee = models.OneToOneField(EmployeeBasic, related_name="solar_system_category_choice", on_delete=models.PROTECT,verbose_name=_("employee_name"))
    category = models.IntegerField(_("المجموعة"), choices=CAT_CHOICES)

    def __str__(self) -> str:
        return f'نوع منظومة الطاقة الشمسية: {self.get_category_display()}'

    class Meta:
        verbose_name = _("منظومة الطاقة الشمسية")
        verbose_name_plural = _("منظومة الطاقة الشمسية")
