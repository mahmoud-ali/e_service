from django.db import models
from django.utils.translation import gettext_lazy as _
from hr import models as hr_models
from hr.models import EmployeeBasic, LoggingModel,EmployeeFamily

STATE_DRAFT = 1
STATE_ACCEPTED = 2
STATE_REJECTED = 3

STATE_CHOICES = {
    STATE_DRAFT: _('state_draft'),
    STATE_ACCEPTED: _('state_accepted'),
    STATE_REJECTED: _('state_rejected'),
}

class EmployeeTelegram(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    user_id = models.FloatField(_("user_id"),unique=True)
    phone = models.CharField(_("phone"),max_length=30,unique=True)
    # state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

class EmployeeTelegramRegistration(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    user_id = models.FloatField(_("user_id"),unique=True)
    name = models.CharField(_("employee_name"),max_length=150)
    phone = models.CharField(_("phone"),max_length=30,unique=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

class EmployeeTelegramFamily(LoggingModel):

    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    relation = models.CharField(_("relation"), choices=EmployeeFamily.FAMILY_RELATION_CHOICES,max_length=10)
    name = models.CharField(_("name"),max_length=100)
    tarikh_el2dafa = models.DateField(_("tarikh_el2dafa"),blank=True,null=True)
    attachement_file = models.FileField(_("attachement"),upload_to=hr_models.attachement_path,blank=True,null=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    class Meta:
        verbose_name = _("Employee Family")
        verbose_name_plural = _("Employee Family")

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.get_relation_display()})'
