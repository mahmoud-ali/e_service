from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator,MinValueValidator


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

class LoggingModel(models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

class Department(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",verbose_name=_("user"))
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
    responsible = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_("responsible"), related_name='departments')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Goal")
        verbose_name_plural = _("Goals")
        ordering = ['code']

class Task(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, verbose_name=_("goal"), related_name='tasks')
    year = models.PositiveIntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    name = models.CharField(_("name"), max_length=255)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

class TaskDuration(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_("task"), related_name='duration')
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)

    def __str__(self):
        return f'{self.task} ({self.get_month_display()} {self.task.year})'
    
    class Meta:
        verbose_name = _("TaskDuration")
        verbose_name_plural = _("TaskDurations")

class TaskExecution(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_("task"), related_name='execution')
    percentage = models.PositiveIntegerField(verbose_name=_("percentage"), validators=[MaxValueValidator(limit_value=100)])
    problems = models.TextField(verbose_name=_("problems"), blank=True)

    def __str__(self):
        return f'{self.task} ({self.percentage})'
    
    class Meta:
        verbose_name = _("TaskExecution")
        verbose_name_plural = _("TaskExecutions")
