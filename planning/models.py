from django.db import models
from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator,MinValueValidator

from company_profile.models import LkpCompanyProductionLicenseStatus, LkpCompanyProductionStatus, LkpMineral, LkpNationality, LkpState, TblCompanyProduction, TblCompanyProductionLicense


MONTH_JAN = 1
MONTH_FEB = 2
MONTH_MAR = 3
MONTH_APR = 4
MONTH_MAY = 5
MONTH_JUN = 6
MONTH_JLY = 7
MONTH_AUG = 8
MONTH_SEP = 9
MONTH_OCT = 10
MONTH_NOV = 11
MONTH_DEC = 12

MONTH_CHOICES = {
    MONTH_JAN: _('MONTH_JAN'),
    MONTH_FEB: _('MONTH_FEB'),
    MONTH_MAR: _('MONTH_MAR'),
    MONTH_APR: _('MONTH_APR'),
    MONTH_MAY: _('MONTH_MAY'),
    MONTH_JUN: _('MONTH_JUN'),
    MONTH_JLY: _('MONTH_JLY'),
    MONTH_AUG: _('MONTH_AUG'),
    MONTH_SEP: _('MONTH_SEP'),
    MONTH_OCT: _('MONTH_OCT'),
    MONTH_NOV: _('MONTH_NOV'),
    MONTH_DEC: _('MONTH_DEC'),
}

STATE_DRAFT = 1
STATE_CONFIRMED = 2
STATE_EXPIRED = 3

STATE_CHOICES = {
    STATE_DRAFT: _('state_draft'),
    STATE_CONFIRMED: _('state_confirmed'),
    # STATE_EXPIRED: _('state_expired'),
}

class LoggingModel(models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

class Department(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="planning_department",verbose_name=_("user"),blank=True,null=True)
    name = models.CharField(_("name"),max_length=255)

    def __str__(self):
        return f'{self.name} ({self.user})'
    
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

class Goal(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children',verbose_name=_("parent_goal"),blank=True,null=True)
    code = models.CharField(_("code"),max_length=10)
    name = models.CharField(_("name"),max_length=255)
    outcome = models.TextField(_("outcome"),blank=True,null=True)
    kpi = models.TextField(_("kpi"),blank=True,null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Goal")
        verbose_name_plural = _("Goals")
        ordering = ['code']

class Task(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, verbose_name=_("goal"), related_name='tasks')
    year = models.PositiveIntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    responsible = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_("responsible"), related_name='departments')
    name = models.CharField(_("name"), max_length=255)

    def __str__(self):
        return f'{self.goal.parent} / {self.goal} / {self.name}'
    
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

class TaskDuration(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_("task"), related_name='duration')
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)

    def __str__(self):
        return f'{self.task.name} ({self.get_month_display()} {self.task.year})'
    
    class Meta:
        verbose_name = _("TaskDuration")
        verbose_name_plural = _("TaskDurations")

class TaskAutomation(models.Model):
    TYPE_MANUAL = 1
    TYPE_AUTO = 2

    TYPE_CHOICES = {
        TYPE_MANUAL: _('type_manual'),
        TYPE_AUTO: _('type_auto'),
    }

    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_("task"), related_name='automation')
    type = models.IntegerField(_("type"), choices=TYPE_CHOICES, default=TYPE_MANUAL)
    view = models.CharField(_("view_name"), max_length=255,help_text='admin inline view', null=True,blank=True, default='')
    percent_calculation_method = models.CharField(_("percent_calculation_method"), max_length=255, null=True,blank=True, default='')

    def __str__(self):
        return f'{self.task.name} ({self.view})'
    
    def clean(self):
        if self.type==self.TYPE_MANUAL and not self.view:
            raise ValidationError(
                {"view":_("Enter inline view class")}
            )
        
        if self.type==self.TYPE_AUTO and not self.percent_calculation_method:
            raise ValidationError(
                {"percent_calculation_method":_("Enter calculation method")}
            )
        return super().clean()
    
    class Meta:
        verbose_name = _("TaskAutomation")
        verbose_name_plural = _("TaskAutomations")

class MonthelyReport(LoggingModel):
    year = models.PositiveIntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

class TaskExecution(models.Model):
    report = models.ForeignKey(MonthelyReport, on_delete=models.CASCADE, null=True, verbose_name=_("report"), related_name='monthly_tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_("task"), related_name='execution')
    percentage = models.PositiveIntegerField(verbose_name=_("percentage"), default=0, validators=[MaxValueValidator(limit_value=100)])
    problems = models.TextField(verbose_name=_("problems"), blank=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    def __str__(self):
        return f'{self.task} ({self.percentage})'
    
    class Meta:
        verbose_name = _("TaskExecution")
        verbose_name_plural = _("TaskExecutions")

class TaskExecutionDetail(models.Model):
    task_execution = models.ForeignKey(TaskExecution, on_delete=models.CASCADE, verbose_name=_("task_execution"), related_name='+')

    class Meta:
        abstract = True

############### Production #####################
class CompanyProductionTask(TaskExecutionDetail):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    total_weight = models.FloatField(_("total_weight"))

class TraditionalProductionTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    total_weight = models.FloatField(_("total_weight"))

class TraditionalStateTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    soug = models.IntegerField(_("soug"))
    grabeel = models.IntegerField(_("grabeel"))
    hofra_kabira = models.IntegerField(_("hofra_kabira"))
    abar_khtot_intag = models.IntegerField(_("abar_khtot_intag"))
    ajhizat_bahth = models.IntegerField(_("ajhizat_bahth"))
    mo3dinin_sosal = models.IntegerField(_("mo3dinin_sosal"))
    toahin_ratiba = models.IntegerField(_("toahin_ratiba"))
    toahin_jafa = models.IntegerField(_("toahin_jafa"))

class OtherMineralsTask(TaskExecutionDetail):
    mineral = models.ManyToManyField(LkpMineral,verbose_name=_("mineral"), help_text=_('in ton'))
    total_weight = models.FloatField(_("total_weight"))

class ExportGoldTraditionalTask(TaskExecutionDetail):
    raw_total_weight = models.FloatField(_("raw_total_weight"))
    net_total_weight = models.FloatField(_("net_total_weight"))
    total_dollar = models.FloatField(_("total_dollar"))

class ExportGoldCompanyTask(TaskExecutionDetail):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    raw_total_weight = models.FloatField(_("raw_total_weight"))
    net_total_weight = models.FloatField(_("net_total_weight"))
    no_alloy = models.IntegerField(_("no_alloy"))

class CompanyInfoTask(TaskExecutionDetail):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    nationality = models.ManyToManyField(LkpNationality,verbose_name=_("nationality"),default=[1]) #, on_delete=models.PROTECT
    status = models.ForeignKey(LkpCompanyProductionStatus, on_delete=models.PROTECT,verbose_name=_("status"))

class CompanyLicenseInfoTask(TaskExecutionDetail):
    license  = models.ForeignKey(TblCompanyProductionLicense, on_delete=models.PROTECT,verbose_name=_("license"))    
    license_no = models.CharField(_("License no"),max_length=20)
    license_type = models.IntegerField(_("license_type"),choices=TblCompanyProductionLicense.LICENSE_TYPE_CHOICES,blank=True,null=True)
    date = models.DateField(_("Sign date"))
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    mineral = models.ManyToManyField(LkpMineral,verbose_name=_("mineral"),default=[1])
    area = models.FloatField(_("Area in Kilometers"),blank=True,null=True)
    area_initial = models.FloatField(_("Initial area in Kilometers"),blank=True,null=True,default=0)
    reserve = models.FloatField(_("Reserve in Tones"),blank=True,null=True)
    contract_status  = models.ForeignKey(LkpCompanyProductionLicenseStatus, on_delete=models.PROTECT,verbose_name=_("contract_status"))

############### Tahsil #####################
class TraditionalTahsilTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    total_money = models.FloatField(_("total_money"))

############### Salama #####################


############### Mojtam3ia #####################
