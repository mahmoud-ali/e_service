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
    """
    Model representing an employee's Telegram account information.
    
    This model stores the connection between an employee and their Telegram account,
    after the employee has been approved by the HR department,
    including their unique Telegram user ID and phone number.

    Attributes:
        employee (ForeignKey): Reference to the EmployeeBasic model
        user_id (FloatField): Unique Telegram user ID
        phone (CharField): Employee's phone number (unique)
    """
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    user_id = models.FloatField(_("user_id"),unique=True)
    phone = models.CharField(_("phone"),max_length=30,unique=True)
    # state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

class EmployeeTelegramRegistration(LoggingModel):
    """
    Model representing a pending registration request for an employee's Telegram account.
    
    This model stores registration requests from employees who want to connect their
    Telegram accounts to the system. These requests need to be reviewed and approved
    before the information is moved to the EmployeeTelegram model.

    Attributes:
        employee (ForeignKey): Reference to the EmployeeBasic model
        user_id (FloatField): Unique Telegram user ID
        name (CharField): Employee's full name
        phone (CharField): Employee's phone number (unique)
        state (IntegerField): Current state of the registration request (draft, accepted, or rejected)
    """
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    user_id = models.FloatField(_("user_id"),unique=True)
    name = models.CharField(_("employee_name"),max_length=150)
    phone = models.CharField(_("phone"),max_length=30,unique=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

class EmployeeTelegramFamily(LoggingModel):
    """
    Model representing family member information for employees using the Telegram system.
    
    This model stores details about an employee's family members, including their relationship
    to the employee, name, date of addition, and any supporting documentation. Each record
    requires approval through a state system.

    Attributes:
        employee (ForeignKey): Reference to the EmployeeBasic model
        relation (CharField): Type of family relationship, using choices from EmployeeFamily model
        name (CharField): Name of the family member
        tarikh_el2dafa (DateField): Date when the family member was added (optional)
        attachement_file (FileField): Supporting documentation for the family member (optional)
        state (IntegerField): Current state of the record (draft, accepted, or rejected)
    """
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
