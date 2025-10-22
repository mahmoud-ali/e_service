from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from hr import models as hr_models
from hr.models import MOAHIL_CHOICES, EmployeeBankAccount, EmployeeBasic, LoggingModel,EmployeeFamily
# from django.contrib.auth.models import  Group

# import requests

# TOKEN_ID = settings.TELEGRAM_TOKEN_ID

STATE_DRAFT = 1
STATE_ACCEPTED = 2
STATE_REJECTED = 3

STATE_CHOICES = {
    STATE_DRAFT: _('state_draft'),
    STATE_ACCEPTED: _('state_accepted'),
    STATE_REJECTED: _('state_rejected'),
}

# def send_message(TOKEN_ID, user_id, message):
#     telegram_url = f"https://api.telegram.org/bot{TOKEN_ID}/sendMessage?chat_id={int(user_id)}&text={message}"
#     return requests.get(telegram_url)

# def send_notifications(TOKEN_ID,message):
#     group = Group.objects.get(name='hr_manpower')
#     for user in group.user_set.all():  # Get all users in the group
#         try:
#             employee = EmployeeBasic.objects.get(email= user.email)
#             user_id = employee.employeetelegramregistration_set.first().user_id

#             # print(TOKEN_ID, user_id, message)
#             send_message(TOKEN_ID, user_id, message)
#         except Exception as e:
#             print(e)


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

    # def save(self, *args, **kwargs):
    #     send_notifications(TOKEN_ID=TOKEN_ID,message=f"قام الموظف {self.employee.name} بالتسجيل")
    #     return super().save(*args, **kwargs)

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
    tarikh_el2dafa = models.DateField(_("تاريخ صدور الشهادة"),blank=True,null=True)
    attachement_file = models.FileField(_("attachement"),upload_to=hr_models.attachement_path)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    class Meta:
        verbose_name = _("Employee Family Application")
        verbose_name_plural = _("Employee Family Application")

    # def __str__(self) -> str:
    #     return f'{self.employee.name} ({self.get_relation_display()})'
    def __str__(self) -> str:
        return f'بيانات الاسرة: {self.name}({self.get_relation_display()})'
    
    def clean(self):
        if not self.tarikh_el2dafa:
            raise ValidationError({
                'tarikh_el2dafa':_("الرجاء إدخال تاريخ صدور الشهادة"),
            })
        return super().clean()

    # def save(self, *args, **kwargs):
    #     send_notifications(TOKEN_ID=TOKEN_ID,message=f"قام الموظف {self.employee.name} بإضافة بيانات اسرة")
    #     return super().save(*args, **kwargs)

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
    attachement_file = models.FileField(_("attachement"),upload_to=hr_models.attachement_path)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    
    class Meta:
        verbose_name = _("Employee Moahil Application")
        verbose_name_plural = _("Employee Moahil Application")

    # def __str__(self) -> str:
    #     return f'{self.employee.name} ({self.get_moahil_display()})'
    def __str__(self) -> str:
        return f'بيانات المؤهل: {self.get_moahil_display()}'

    # def save(self, *args, **kwargs):
    #     send_notifications(TOKEN_ID=TOKEN_ID,message=f"قام الموظف {self.employee.name} بإضافة بيانات مؤهل")
    #     return super().save(*args, **kwargs)

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

    # def __str__(self) -> str:
    #     return f'{self.employee.name} ({EmployeeBankAccount.BANK_CHOICES[self.bank]})'# / {self.edara_3ama.name}'
    def __str__(self) -> str:
        return f'رقم حساب: {self.account_no} - ({self.get_bank_display()})'

    def clean(self):
        if EmployeeBankAccount.objects.filter(account_no=self.account_no).exists():
            raise ValidationError({
                'account_no':_("رقم الحساب مدخل مسبقاً"),
            })
        
        if (self.bank == EmployeeBankAccount.BANK_KHARTOUM and len(self.account_no) != 16):
            raise ValidationError({
                'account_no':_("الرجاء إدخال حساب مكون من 16 خانة"),
            })
        
        if (self.bank == EmployeeBankAccount.BANK_OMDURMAN and (len(self.account_no) != 5 and len(self.account_no) != 6 and len(self.account_no) != 7)):
            raise ValidationError({
                'account_no':_("الرجاء إدخال حساب مكون من 5 - 7 خانات"),
            })
        
        return super().clean()

    # def save(self, *args, **kwargs):
    #     send_notifications(TOKEN_ID=TOKEN_ID,message=f"قام الموظف {self.employee.name} بإضافة بيانات حساب بنكي")
    #     return super().save(*args, **kwargs)

class EmployeeBasicProxy(hr_models.EmployeeBasic):
    class Meta:
        proxy = True
        verbose_name = _("Employee data")
        verbose_name_plural = _("Employee data")

class EmployeeBankAccountProxy(hr_models.EmployeeBankAccount):
    class Meta:
        proxy = True
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")

class EmployeeFamilyProxy(hr_models.EmployeeFamily):
    class Meta:
        proxy = True
        verbose_name = _("Employee Family")
        verbose_name_plural = _("Employee Family")

class EmployeeMoahilProxy(hr_models.EmployeeMoahil):
    class Meta:
        proxy = True
        verbose_name = _("Employee Moahil")
        verbose_name_plural = _("Employee Moahil")

class SalafiatProxy(hr_models.EmployeeSalafiat):
    class Meta:
        proxy = True
        verbose_name = _("Salafiat")
        verbose_name_plural = _("Salafiat")

class JazaatProxy(hr_models.EmployeeJazaat):
    class Meta:
        proxy = True
        verbose_name = _("Jazaat")
        verbose_name_plural = _("Jazaat")

class ApplicationRequirement(models.Model):
    ATFAL = 1
    GASIMA = 2
    MOAHIL = 3
    BANK_ACCOUNT = 4

    APP_CHOICES = {
        ATFAL: _("إضافة طفل"),
        GASIMA: _("إضافة قسيمة"),
        MOAHIL: _("إضافة مؤهل"),
        BANK_ACCOUNT: _("إضافة حساب بنكي"),
    }
    app = models.PositiveSmallIntegerField(_("الطلب"),choices=APP_CHOICES)
    requirement = models.CharField(_("المتطلبات"),max_length=255)

    def __str__(self) -> str:
        return f"{self.app}: {self.requirement}"

    class Meta:
        verbose_name = _("مطلوبات الاجراءات")
        verbose_name_plural = _("مطلوبات الاجراءات")