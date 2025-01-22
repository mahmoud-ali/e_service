from django.db import models
from django.utils.translation import gettext_lazy as _
from hr import models as hr_models
from hr.models import MOAHIL_CHOICES, EmployeeBankAccount, EmployeeBasic, LoggingModel,EmployeeFamily

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

    class Meta:
        verbose_name = _("Employee Telegram")
        verbose_name_plural = _("Employee Telegram")

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

    class Meta:
        verbose_name = _("Employee Registration")
        verbose_name_plural = _("Employee Registration")

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
        verbose_name = _("Employee Family Application")
        verbose_name_plural = _("Employee Family Application")

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.get_relation_display()})'

class EmployeeTelegramMoahil(LoggingModel):
    """
    Model representing educational qualifications for employees using the Telegram system.
    
    This model stores information about an employee's educational background and qualifications,
    including their degree type, university, specialization, graduation date, and supporting
    documentation. Each qualification record requires approval through a state system.

    Attributes:
        employee (ForeignKey): Reference to the EmployeeBasic model
        moahil (CharField): Type of educational qualification/degree
        university (CharField): Name of the university or educational institution
        takhasos (CharField): Field of specialization or major
        graduate_dt (DateField): Date of graduation
        tarikh_el2dafa (DateField): Date when the qualification was added (optional)
        attachement_file (FileField): Supporting documentation for the qualification (optional)
        state (IntegerField): Current state of the record (draft, accepted, or rejected)
    """
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    moahil = models.CharField(_("moahil"), choices=MOAHIL_CHOICES,max_length=20)
    university = models.CharField(_("university"),max_length=150)
    takhasos = models.CharField(_("takhasos"),max_length=100)
    graduate_dt = models.DateField(_("graduate_dt"))
    tarikh_el2dafa = models.DateField(_("tarikh_el2dafa"),blank=True,null=True)
    attachement_file = models.FileField(_("attachement"),upload_to=hr_models.attachement_path,blank=True,null=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    
    class Meta:
        verbose_name = _("Employee Moahil Application")
        verbose_name_plural = _("Employee Moahil Application")

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.get_moahil_display()})'

class EmployeeTelegramBankAccount(LoggingModel):
    """
    Model representing bank account information for employees using the Telegram system.
    
    This model stores banking details for employees, including their bank selection,
    account number, and active status. Each bank account record requires approval
    through a state system.

    Attributes:
        employee (ForeignKey): Reference to the EmployeeBasic model
        bank (CharField): Selected bank from predefined choices in EmployeeBankAccount model
        account_no (CharField): Employee's bank account number
        active (BooleanField): Indicates if this is the currently active bank account
        state (IntegerField): Current state of the record (draft, accepted, or rejected)
    """
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    bank = models.CharField(_("bank"), choices=EmployeeBankAccount.BANK_CHOICES,max_length=10)
    account_no = models.CharField(_("account_no"),max_length=20)
    active = models.BooleanField(_("active"),default=False)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    class Meta:
        verbose_name = _("Bank Account Application")
        verbose_name_plural = _("Bank Account Application")

    def __str__(self) -> str:
        return f'{self.employee.name} ({EmployeeBankAccount.BANK_CHOICES[self.bank]})'# / {self.edara_3ama.name}'

class EmployeeBasicProxy(hr_models.EmployeeBasic):
    class Meta:
        proxy = True
        verbose_name = _("Employee data")
        verbose_name_plural = _("Employee data")

class EmployeeBankAccountProxy(hr_models.EmployeeBankAccount):
    class Meta:
        proxy = True

class EmployeeFamilyProxy(hr_models.EmployeeFamily):
    class Meta:
        proxy = True

class EmployeeMoahilProxy(hr_models.EmployeeMoahil):
    class Meta:
        proxy = True

class SalafiatProxy(hr_models.EmployeeSalafiat):
    class Meta:
        proxy = True

class JazaatProxy(hr_models.EmployeeJazaat):
    class Meta:
        proxy = True
