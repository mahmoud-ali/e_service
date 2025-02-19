"""
Planning and Reporting System Models

This module defines a comprehensive system for managing annual planning and monthly 
execution tracking across multiple operational domains. The system includes:

Core Components:
- LoggingModel: Abstract base model with audit fields (created/updated timestamps and users)
- Goal/Task hierarchy: Tree-structured objectives with annual department assignments
- YearlyPlanning: Master container for annual plans with monthly breakdowns
- MonthelyReport: Execution tracking with detailed task completion records

Main Model Groups:
1. Planning Models (YearlyPlanning & Related):
   - Production planning (company, traditional, minerals)
   - Financial collection planning (tahsil)
   - Gold export projections

2. Reporting Models (MonthelyReport & Related):
   - 25+ specialized TaskExecutionDetail subtypes covering:
     * Production metrics       * Safety reports (salama)
     * Incident tracking        * Community obligations
     * Media monitoring         * IT support
     * General management       * Legal matters

Key Features:
- Hierarchical goal system with parent/child relationships
- Polymorphic reporting through TaskExecutionDetail subclasses
- Automated task tracking rules (TaskAutomation)
- Localization support with Arabic translations
- Validation rules for data integrity (year ranges, percentages, required fields)
- Audit trails for all changes through LoggingModel inheritance
"""

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

class LoggingModel(models.Model):
    """Abstract base model providing audit trail fields for creation and modification tracking.
    
    Fields:
        created_at - Auto-set DateTime when record was created
        created_by - User who created the record (protected FK)
        updated_at - Auto-updated DateTime when record was last modified
        updated_by - User who last modified the record (protected FK)
        
    Inherited by all planning/reporting models to maintain audit history.
    """
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

class Department(models.Model):
    """Represents organizational departments and their user associations.
    
    Fields:
        user - OneToOne relationship mapping users to departments (optional)
        name - Department name (max 255 chars)
        
    Used to assign responsibilities in planning and reporting workflows.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="planning_department",verbose_name=_("user"),blank=True,null=True)
    name = models.CharField(_("name"),max_length=255)

    def __str__(self):
        return f'{self.name} ({self.user})'
    
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

class Goal(models.Model):
    """Hierarchical organizational objectives with parent-child relationships.
    
    Fields:
        parent - Optional parent goal (self-referential FK)
        code - Short identifier code (max 10 chars)
        name - Goal name (max 255 chars)
        outcome - Description of desired outcomes
        kpi - Key Performance Indicators for tracking
        
    Forms a tree structure of organizational goals and sub-goals.
    """
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
    """Annual departmental task linked to specific goals.
    
    Fields:
        goal - Parent goal this task supports (FK to Goal)
        year - Validated year range 2015-2100
        responsible - Department accountable for completion (FK to Department)
        name - Task description (max 255 chars)
        
    Related:
        duration - Monthly breakdowns via TaskDuration
    """
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, verbose_name=_("goal"), related_name='tasks')
    year = models.PositiveIntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    responsible = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_("responsible"), related_name='departments')
    name = models.CharField(_("name"), max_length=255)

    def __str__(self):
        return f'{self.goal.parent} / {self.goal} / {self.name} ({self.responsible.name})'
    
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

class TaskDuration(models.Model):
    """Monthly duration tracking for annual tasks.
    
    Fields:
        task - Parent task (FK to Task)
        month - Month number (1-12) with translated display names
        
    Provides monthly breakdown of task execution timelines.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_("task"), related_name='duration')
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)

    def __str__(self):
        return f'{self.task.name} ({self.get_month_display()} {self.task.year})'
    
    class Meta:
        verbose_name = _("TaskDuration")
        verbose_name_plural = _("TaskDurations")

class TaskAutomation(models.Model):
    """Defines automation rules for task tracking and progress calculation.
    
    Fields:
        task - Task to automate (FK to Task)
        type - Automation type: Manual (1) or Auto (2)
        view - Admin inline view name (required for manual)
        percent_calculation_method - Calculation logic (required for auto)
        
    Validation ensures required fields based on automation type.
    """
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

############### Planning ##################
class YearlyPlanning(LoggingModel):
    """Master record for annual planning data and status.
    
    Fields:
        year - Validated year range 2015-2100
        state - Planning state: Draft (1) or Confirmed (2)
        
    Serves as container for all monthly planning breakdowns.
    """
    year = models.PositiveIntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    class Meta:
        verbose_name = _("YearlyPlanning")
        verbose_name_plural = _("YearlyPlanning")

class CompanyProductionMonthlyPlanning(models.Model):
    """Monthly planned production targets for company operations.
    
    Fields:
        plan - Parent yearly plan (FK to YearlyPlanning)
        month - Month number (1-12)
        planed_weight - Planned production weight
        
    Part of yearly planning breakdown for company production.
    """
    plan = models.ForeignKey(YearlyPlanning, on_delete=models.CASCADE, verbose_name=_("plan"), related_name='+')
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    planed_weight = models.FloatField(_("planed_weight"))

    class Meta:
        verbose_name = _("CompanyProductionMonthlyPlanning")
        verbose_name_plural = _("CompanyProductionMonthlyPlanning")

class TraditionaProductionMonthlyPlanning(models.Model):
    plan = models.ForeignKey(YearlyPlanning, on_delete=models.CASCADE, verbose_name=_("plan"), related_name='+')
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    planed_weight = models.FloatField(_("planed_weight"))

    class Meta:
        verbose_name = _("TraditionaProductionMonthlyPlanning")
        verbose_name_plural = _("TraditionaProductionMonthlyPlanning")

class OtherMineralsProductionMonthlyPlanning(models.Model):
    plan = models.ForeignKey(YearlyPlanning, on_delete=models.CASCADE, verbose_name=_("plan"), related_name='+')
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    mineral = models.ForeignKey(LkpMineral, on_delete=models.PROTECT,verbose_name=_("mineral"), help_text=_('in ton'))
    planed_weight = models.FloatField(_("planed_weight"))

    class Meta:
        verbose_name = _("OtherMineralsProductionMonthlyPlanning")
        verbose_name_plural = _("OtherMineralsProductionMonthlyPlanning")

class TraditionaTahsilMonthlyPlanning(models.Model):
    plan = models.ForeignKey(YearlyPlanning, on_delete=models.CASCADE, verbose_name=_("plan"), related_name='+')
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    planed_money = models.FloatField(_("planed_money"))

    class Meta:
        verbose_name = _("TraditionaTahsilMonthlyPlanning")
        verbose_name_plural = _("TraditionaTahsilMonthlyPlanning")

class TraditionaTahsilByBandMonthlyPlanning(models.Model):
    plan = models.ForeignKey(YearlyPlanning, on_delete=models.CASCADE, verbose_name=_("plan"), related_name='+')
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    band = models.IntegerField(_("band"),choices=BAND_CHOICES)
    planed_money = models.FloatField(_("planed_money"))

    class Meta:
        verbose_name = _("TraditionaTahsilByBandMonthlyPlanning")
        verbose_name_plural = _("TraditionaTahsilByBandMonthlyPlanning")

class TraditionaTahsilByJihaMonthlyPlanning(models.Model):
    plan = models.ForeignKey(YearlyPlanning, on_delete=models.CASCADE, verbose_name=_("plan"), related_name='+')
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    jiha = models.IntegerField(_("jiha"),choices=JIHA_CHOICES)
    planed_money = models.FloatField(_("planed_money"))

    class Meta:
        verbose_name = _("TraditionaTahsilByJihaMonthlyPlanning")
        verbose_name_plural = _("TraditionaTahsilByJihaMonthlyPlanning")

class ExportGoldTraditionalMonthlyPlanning(models.Model):
    plan = models.ForeignKey(YearlyPlanning, on_delete=models.CASCADE, verbose_name=_("plan"), related_name='+')
    raw_total_weight = models.FloatField(_("raw_total_weight"))
    net_total_weight = models.FloatField(_("net_total_weight"))

    class Meta:
        verbose_name = _("ExportGoldTraditionalMonthlyPlanning")
        verbose_name_plural = _("ExportGoldTraditionalMonthlyPlanning")

class ExportGoldCompanyMonthlyPlanning(models.Model):
    plan = models.ForeignKey(YearlyPlanning, on_delete=models.CASCADE, verbose_name=_("plan"), related_name='+')
    raw_total_weight = models.FloatField(_("raw_total_weight"))
    net_total_weight = models.FloatField(_("net_total_weight"))

    class Meta:
        verbose_name = _("ExportGoldCompanyMonthlyPlanning")
        verbose_name_plural = _("ExportGoldCompanyMonthlyPlanning")

############ Monthly Report #############
class MonthelyReport(LoggingModel):
    """Monthly execution tracking and reporting container.
    
    Fields:
        year - Validated year range 2015-2100
        month - Month number (1-12)
        state - Report state: Draft (1) or Confirmed (2)
        
    Contains task execution details and progress tracking.
    """
    year = models.PositiveIntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    def __str__(self):
        state = ''
        # if self.state == STATE_DRAFT:
        #     state = f' ({self.get_state_display()})'

        return f'{self.get_month_display()} {self.year}'+state

class TaskExecution(LoggingModel):
    """Tracks progress and status of task completion for monthly reports.
    
    Fields:
        report - Parent monthly report (FK to MonthelyReport)
        task - Reference task (FK to Task)
        percentage - Completion percentage (0-100)
        problems - Description of any issues encountered
        state - Execution state: Draft (1) or Confirmed (2)
    """
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
    """Abstract base model for detailed task execution tracking.
    
    Fields:
        task_execution - Parent task execution record (FK to TaskExecution)
        
    Inherited by specialized execution detail models covering different domains.
    """
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
    # total_dollar = models.FloatField(_("total_dollar"))

    class Meta:
        verbose_name = _("ExportGoldTraditionalTask")
        verbose_name_plural = _("ExportGoldTraditionalTasks")

class ExportGoldCompanyTask(TaskExecutionDetail):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    raw_total_weight = models.FloatField(_("raw_total_weight"))
    net_total_weight = models.FloatField(_("net_total_weight"))
    # no_alloy = models.IntegerField(_("no_alloy"))

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

class ExplorationMapTask(TaskExecutionDetail):
    def attachement_path(self, filename):
        year = self.task_execution.report.year
        month = self.task_execution.report.month
        return "planning/{0}/{1}/{2}".format(year,month, filename)    

    is_new_map = models.BooleanField(_("is_new_map_exists"))
    map = models.ImageField(_("exploration_map"),upload_to=attachement_path,null=True,blank=True)
    map_description = models.TextField(_("map_description"),blank=True,null=True)

    class Meta:
        verbose_name = _("ExplorationMapTask")
        verbose_name_plural = _("ExplorationMapTasks")

    def clean(self):
        if self.is_new_map:
            if not self.map:
                raise ValidationError(
                    {"map":_('Field required')}
                )

            if not self.map_description:
                raise ValidationError(
                    {"map_description":_('Field required')}
                )

        return super().clean()

############### Tahsil #####################
class TraditionalTahsilTask(TaskExecutionDetail):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    total_money = models.FloatField(_("total_money"))

    class Meta:
        verbose_name = _("TraditionalTahsilTask")
        verbose_name_plural = _("TraditionalTahsilTasks")

class TahsilByBandTask(TaskExecutionDetail):
    band = models.IntegerField(_("band"),choices=BAND_CHOICES)
    total_money = models.FloatField(_("total_money"))

    class Meta:
        verbose_name = _("TahsilByBandTask")
        verbose_name_plural = _("TahsilByBandTasks")

class TahsilByJihaTask(TaskExecutionDetail):
    jiha = models.IntegerField(_("jiha"),choices=JIHA_CHOICES)
    total_money = models.FloatField(_("total_money"))
    planed_money = models.FloatField(_("planed_money"))

    class Meta:
        verbose_name = _("TahsilByJihaTask")
        verbose_name_plural = _("TahsilByJihaTasks")

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
    """Tracks company accident reports (7oadith = حوادث = accidents)
    
    Fields:
        company - Company reference (FK to TblCompanyProduction)
        no_7oadith - Number of accidents reported
        
    Part of safety reporting system for company operations
    """
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    no_7oadith = models.IntegerField(_("no_7oadith"))

    class Meta:
        verbose_name = _("Company7oadithTask")
        verbose_name_plural = _("Company7oadithTasks")

class Traditional7oadthTask(TaskExecutionDetail):
    """Tracks traditional mining sector incidents (7oadth = حوادث = incidents)
    
    Fields:
        state - State/province reference (FK to LkpState)
        no_wafiat - Number of fatalities (wafiat = وفيات)
        no_7oadith - Number of incidents
        no_e9abat - Number of injuries (e9abat = إصابات)
        
    Part of safety reporting for traditional mining operations
    """
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    no_wafiat = models.IntegerField(_("no_wafiat"))
    no_7oadith = models.IntegerField(_("no_7oadith"))
    no_e9abat = models.IntegerField(_("no_e9abat"))

    class Meta:
        verbose_name = _("Traditional7oadthTask")
        verbose_name_plural = _("Traditional7oadthTasks")

class CompanyMokhalafatTask(TaskExecutionDetail):
    """Tracks company violations and resolutions (Mokhalafat = مخالفات = violations)
    
    Fields:
        company - Company reference (FK to TblCompanyProduction)
        no_mokhalafat - Number of violations identified
        no_mokhalafat_fixed - Number of violations resolved
        
    Part of compliance monitoring system
    """
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    no_mokhalafat = models.IntegerField(_("no_mokhalafat"))
    no_mokhalafat_fixed = models.IntegerField(_("no_mokhalafat_fixed"))

    class Meta:
        verbose_name = _("CompanyMokhalafatTask")
        verbose_name_plural = _("CompanyMokhalafatTasks")

############### Mojtam3ia #####################
class Mas2oliaMojtama3iaTask(TaskExecutionDetail):
    """Tracks community obligation fulfillment (Mas2olia Mojtama3ia = مسؤولية مجتمعية = social responsibility)
    
    Fields:
        state - State/province reference (FK to LkpState)
        locality - Local community name
        amount - Financial amount allocated
        
    Monitors company commitments to local communities
    """
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    locality = models.CharField(_("locality"), max_length=50)
    amount = models.FloatField(_("amount"))

    class Meta:
        verbose_name = _("Mas2oliaMojtama3iaTask")
        verbose_name_plural = _("Mas2oliaMojtama3iaTasks")

############## Media #######################
class MediaRasdBathTask(TaskExecutionDetail):
    """Media monitoring task (Rasd Bath = رصد باث = broadcast monitoring)
    
    Fields:
        no3_bath - Type of media broadcast (1: TV, 2: Radio, 3: Online)
        count - Total media mentions
        count_positive - Positive/neutral mentions
        
    Tracks company presence in media outlets
    """
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3

    NO3_BATH_CHOICES = {
        TYPE_1:_('no3_bath_1'),
        TYPE_2:_('no3_bath_2'),
        TYPE_3:_('no3_bath_3'),
    }

    no3_bath = models.IntegerField(_("no3_bath"), choices=NO3_BATH_CHOICES)

    count  =models.IntegerField(_("count"))    
    count_positive  =models.IntegerField(_("count_positive"))    
    
    class Meta:
        verbose_name = _("MediaRasdBathTask")
        verbose_name_plural = _("MediaRasdBathTasks")

class MediaF2atMostakhdmaTask(TaskExecutionDetail):
    """Media segment analysis task (F2at Mostakhdma = فقعات مستخدمة = used segments)
    
    Fields:
        type - Media type (1: News, 2: Opinion, 3: Advertisement, 4: Social, 5: Other)
        count - Number of media segments
        
    Tracks company-related media content analysis
    """
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4
    TYPE_5 = 5

    NO3_BATH_CHOICES = {
        TYPE_1:_('no3_media_mostathmir_1'),
        TYPE_2:_('no3_media_mostathmir_2'),
        TYPE_3:_('no3_media_mostathmir_3'),
        TYPE_4:_('no3_media_mostathmir_4'),
        TYPE_5:_('no3_media_mostathmir_5'),
    }

    type = models.IntegerField(_("type"), choices=NO3_BATH_CHOICES)

    count  =models.IntegerField(_("count"))    
    
    class Meta:
        verbose_name = _("MediaF2atMostakhdmaTask")
        verbose_name_plural = _("MediaF2atMostakhdmaTasks")

class MediaDiscoveryTask(TaskExecutionDetail):
    """Media discovery monitoring task (Discovery = اكتشاف = discovery)
    
    Fields:
        type - Discovery type (1: New sites, 2: Exploration, 3: Research, 4: Tech, 5: Other)
        count - Number of discoveries
        
    Tracks mineral exploration and geological discoveries
    """
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4
    TYPE_5 = 5

    NO3_BATH_CHOICES = {
        TYPE_1:_('no3_discovery_1'),
        TYPE_2:_('no3_discovery_2'),
        TYPE_3:_('no3_discovery_3'),
        TYPE_4:_('no3_discovery_4'),
        TYPE_5:_('no3_discovery_5'),
    }

    type = models.IntegerField(_("type"), choices=NO3_BATH_CHOICES)

    count  =models.IntegerField(_("count"))    
    
    class Meta:
        verbose_name = _("MediaDiscoveryTask")
        verbose_name_plural = _("MediaDiscoveryTasks")

############## IT #######################
class MediaITSupportTask(TaskExecutionDetail):
    """IT support request tracking task
    
    Fields:
        type - Support type:
            1: Network, 2: Hardware, 3: Software, 4: Security,
            5: Data, 6: Training, 7: Reporting, 8: Integration,
            9: Maintenance, 10: Other
        count - Number of support requests
        
    Tracks IT department service requests and issues
    """
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4
    TYPE_5 = 5
    TYPE_6 = 6
    TYPE_7 = 7
    TYPE_8 = 8
    TYPE_9 = 9
    TYPE_10 = 10

    NO3_BATH_CHOICES = {
        TYPE_1:_('no3_it_support_1'),
        TYPE_2:_('no3_it_support_2'),
        TYPE_3:_('no3_it_support_3'),
        TYPE_4:_('no3_it_support_4'),
        TYPE_5:_('no3_it_support_5'),
        TYPE_6:_('no3_it_support_6'),
        TYPE_7:_('no3_it_support_7'),
        TYPE_8:_('no3_it_support_8'),
        TYPE_9:_('no3_it_support_9'),
        TYPE_10:_('no3_it_support_10'),
    }

    type = models.IntegerField(_("type"), choices=NO3_BATH_CHOICES)

    count  =models.IntegerField(_("count"))    
    
    class Meta:
        verbose_name = _("MediaITSupportTask")
        verbose_name_plural = _("MediaITSupportTasks")


################ GM #########################
class GMTask(TaskExecutionDetail):
    """General Management task tracking
    
    Fields:
        type - Task type:
            1: Strategy, 2: Budgeting, 3: Reporting,
            4: Compliance, 5: Audit, 6: HR, 7: Other
        count - Number of tasks completed
        comments - Additional notes
        
    Tracks high-level management activities and initiatives
    """
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4
    TYPE_5 = 5
    TYPE_6 = 6
    TYPE_7 = 7

    NO3_BATH_CHOICES = {
        TYPE_1:_('gm_task_1'),
        TYPE_2:_('gm_task_2'),
        TYPE_3:_('gm_task_3'),
        TYPE_4:_('gm_task_4'),
        TYPE_5:_('gm_task_5'),
        TYPE_6:_('gm_task_6'),
        TYPE_7:_('gm_task_7'),
    }

    type = models.IntegerField(_("type"), choices=NO3_BATH_CHOICES)
    count  =models.IntegerField(_("count"))    
    comments = models.TextField(_("comments"))

    class Meta:
        verbose_name = _("GMTask")
        verbose_name_plural = _("GMTasks")

################ Ganonia ####################
class GanoniaTask(TaskExecutionDetail):
    """Legal matters tracking (Ganonia = جنائية = criminal/legal)
    
    Fields:
        type - Legal case type:
            1: Contract, 2: Labor, 3: Environmental,
            4: Safety, 5: Tax, 6: Compliance, 7: Other
        count - Number of legal cases/matters
        
    Monitors legal issues and regulatory compliance cases
    """
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4
    TYPE_5 = 5
    TYPE_6 = 6
    TYPE_7 = 7

    NO3_BATH_CHOICES = {
        TYPE_1:_('ganonia_task_1'),
        TYPE_2:_('ganonia_task_2'),
        TYPE_3:_('ganonia_task_3'),
        TYPE_4:_('ganonia_task_4'),
        TYPE_5:_('ganonia_task_5'),
        TYPE_6:_('ganonia_task_6'),
        TYPE_7:_('ganonia_task_7'),
    }

    type = models.IntegerField(_("type"), choices=NO3_BATH_CHOICES)

    count  =models.IntegerField(_("count"))    
    
    class Meta:
        verbose_name = _("GanoniaTask")
        verbose_name_plural = _("GanoniaTasks")

