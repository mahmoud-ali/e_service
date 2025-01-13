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

    class Meta:
        verbose_name = _("CompanyProductionTask")
        verbose_name_plural = _("CompanyProductionTasks")

class TraditionalProductionTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    total_weight = models.FloatField(_("total_weight"))

    class Meta:
        verbose_name = _("TraditionalProductionTask")
        verbose_name_plural = _("TraditionalProductionTasks")

class TraditionalStateTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    soug = models.IntegerField(_("no_soug"))
    grabeel = models.IntegerField(_("no_grabeel"))
    hofra_kabira = models.IntegerField(_("no_hofra_kabira"))
    abar_khtot_intag = models.IntegerField(_("no_abar_khtot_intag"))
    ajhizat_bahth = models.IntegerField(_("no_ajhizat_bahth"))
    mo3dinin_sosal = models.IntegerField(_("no_mo3dinin_sosal"))
    toahin_ratiba = models.IntegerField(_("no_toahin_ratiba"))
    toahin_jafa = models.IntegerField(_("no_toahin_jafa"))

    class Meta:
        verbose_name = _("TraditionalStateTask")
        verbose_name_plural = _("TraditionalStateTasks")

class OtherMineralsTask(TaskExecutionDetail):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    mineral = models.ForeignKey(LkpMineral, on_delete=models.PROTECT,verbose_name=_("mineral"), help_text=_('in ton'))
    total_weight = models.FloatField(_("total_weight"))

    class Meta:
        verbose_name = _("OtherMineralsTask")
        verbose_name_plural = _("OtherMineralsTasks")

class ExportGoldTraditionalTask(TaskExecutionDetail):
    raw_total_weight = models.FloatField(_("raw_total_weight"))
    net_total_weight = models.FloatField(_("net_total_weight"))
    total_dollar = models.FloatField(_("total_dollar"))

    class Meta:
        verbose_name = _("ExportGoldTraditionalTask")
        verbose_name_plural = _("ExportGoldTraditionalTasks")

class ExportGoldCompanyTask(TaskExecutionDetail):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    raw_total_weight = models.FloatField(_("raw_total_weight"))
    net_total_weight = models.FloatField(_("net_total_weight"))
    no_alloy = models.IntegerField(_("no_alloy"))

    class Meta:
        verbose_name = _("ExportGoldCompanyTask")
        verbose_name_plural = _("ExportGoldCompanyTasks")

class CompanyInfoTask(TaskExecutionDetail):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    nationality = models.ManyToManyField(LkpNationality,verbose_name=_("nationality"),default=[1]) #, on_delete=models.PROTECT
    status = models.ForeignKey(LkpCompanyProductionStatus, on_delete=models.PROTECT,verbose_name=_("status"))

    class Meta:
        verbose_name = _("CompanyInfoTask")
        verbose_name_plural = _("CompanyInfoTasks")

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

    class Meta:
        verbose_name = _("CompanyLicenseInfoTask")
        verbose_name_plural = _("CompanyLicenseInfoTasks")

############### Tahsil #####################
class TraditionalTahsilTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    total_money = models.FloatField(_("total_money"))

    class Meta:
        verbose_name = _("TraditionalTahsilTask")
        verbose_name_plural = _("TraditionalTahsilTasks")

class TraditionalTahsilByBandTask(TaskExecutionDetail):
    BAND_1 = 1
    BAND_2 = 2
    BAND_3 = 3
    BAND_4 = 4
    BAND_5 = 5
    BAND_6 = 6
    BAND_7 = 7
    BAND_8 = 8
    BAND_9 = 9
    BAND_10 = 10
    BAND_11 = 11
    BAND_12 = 12
    BAND_13 = 13
    BAND_14 = 14
    BAND_15 = 15
    BAND_16 = 16

    BAND_CHOICES = {
        BAND_1:_('band_1'),
        BAND_2:_('band_2'),
        BAND_3:_('band_3'),
        BAND_4:_('band_4'),
        BAND_5:_('band_5'),
        BAND_6:_('band_6'),
        BAND_7:_('band_7'),
        BAND_8:_('band_8'),
        BAND_9:_('band_9'),
        BAND_10:_('band_10'),
        BAND_11:_('band_11'),
        BAND_12:_('band_12'),
        BAND_13:_('band_13'),
        BAND_14:_('band_14'),
        BAND_15:_('band_15'),
        BAND_16:_('band_16'),
    }

    band = models.IntegerField(_("band"),choices=BAND_CHOICES)
    total_money = models.FloatField(_("total_money"))

    class Meta:
        verbose_name = _("TraditionalTahsilByBandTask")
        verbose_name_plural = _("TraditionalTahsilByBandTasks")

class TraditionalTahsilByJihaTask(TaskExecutionDetail):
    JIHA_1 = 1
    JIHA_2 = 2
    JIHA_3 = 3
    JIHA_4 = 4
    JIHA_5 = 5

    JIHA_CHOICES = {
        JIHA_1:_('jiha_1'),
        JIHA_2:_('jiha_2'),
        JIHA_3:_('jiha_3'),
        JIHA_4:_('jiha_4'),
        JIHA_5:_('jiha_5'),
    }

    jiha = models.IntegerField(_("jiha"),choices=JIHA_CHOICES)
    total_money = models.FloatField(_("total_money"))

    class Meta:
        verbose_name = _("TraditionalTahsilByJihaTask")
        verbose_name_plural = _("TraditionalTahsilByJihaTasks")

############### Salama #####################

class TraditionalSalamaMatlobatTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    taswir_asag = models.FloatField(_("taswir_asag"))
    trhil_karta = models.FloatField(_("trhil_karta"))
    slamat_manajim = models.FloatField(_("slamat_manajim"))
    no_3iadat = models.FloatField(_("no_3iadat"))
    no_is3af = models.FloatField(_("no_is3af"))
    t3mol_zi2bag = models.FloatField(_("t3mol_zi2bag"))

    class Meta:
        verbose_name = _("TraditionalSalamaMatlobatTask")
        verbose_name_plural = _("TraditionalSalamaMatlobatTasks")

class TraditionalSalamaRagabaTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    m2moriat_taftishia = models.FloatField(_("m2moriat_taftishia"))
    lig2at_2rshadia = models.FloatField(_("lig2at_2rshadia"))
    taslim_tgarir = models.FloatField(_("taslim_tgarir"))

    class Meta:
        verbose_name = _("TraditionalSalamaRagabaTask")
        verbose_name_plural = _("TraditionalSalamaRagabaTasks")

class CompanySalamaMatlobatTask(TaskExecutionDetail):
    NASHAT_1 = 1
    NASHAT_2 = 2
    NASHAT_3 = 3
    NASHAT_4 = 4
    NASHAT_5 = 5
    NASHAT_6 = 6

    NASHAT_CHOICES = {
        NASHAT_1:_('nashat_1'),
        NASHAT_2:_('nashat_2'),
        NASHAT_3:_('nashat_3'),
        NASHAT_4:_('nashat_4'),
        NASHAT_5:_('nashat_5'),
        NASHAT_6:_('nashat_6'),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    nashat = models.IntegerField(_("nashat"),choices=NASHAT_CHOICES)
    percent = models.FloatField(_("percent"))

    class Meta:
        verbose_name = _("CompanySalamaMatlobatTask")
        verbose_name_plural = _("CompanySalamaMatlobatTasks")

class Company7oadithTask(TaskExecutionDetail):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    no_7oadith = models.IntegerField(_("no_7oadith"))

    class Meta:
        verbose_name = _("Company7oadithTask")
        verbose_name_plural = _("Company7oadithTasks")

class Traditional7oadthTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    no_wafiat = models.IntegerField(_("no_wafiat"))
    no_7oadith = models.IntegerField(_("no_7oadith"))
    no_e9abat = models.IntegerField(_("no_e9abat"))

    class Meta:
        verbose_name = _("Traditional7oadthTask")
        verbose_name_plural = _("Traditional7oadthTasks")

class CompanyMokhalafatTask(TaskExecutionDetail):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    no_mokhalafat = models.IntegerField(_("no_mokhalafat"))
    no_mokhalafat_fixed = models.IntegerField(_("no_mokhalafat_fixed"))

    class Meta:
        verbose_name = _("CompanyMokhalafatTask")
        verbose_name_plural = _("CompanyMokhalafatTasks")

############### Mojtam3ia #####################
