import sys
from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _

from planning.forms import DepartmentForm
from planning.utils import get_company_types

from .models import STATE_DRAFT, CompanyProductionMonthlyPlanning, ExportGoldCompanyMonthlyPlanning, ExportGoldTraditionalMonthlyPlanning, Goal, Department, MonthelyReport, OtherMineralsProductionMonthlyPlanning, Task, TaskAutomation, TaskDuration, TaskExecution, TraditionaProductionMonthlyPlanning, TraditionaTahsilByBandMonthlyPlanning, TraditionaTahsilByJihaMonthlyPlanning, TraditionaTahsilMonthlyPlanning, YearlyPlanning

from .admin_tasks_inline import *

class LogAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    form = DepartmentForm
    list_display = ["user","name"]

class MainGoalFilter(admin.SimpleListFilter):
    title = _("main_goal")    
    parameter_name = "main_goal"
    def lookups(self, request, model_admin):
        qs = Goal.objects.filter(parent__isnull=True).order_by('code').distinct("code").values_list("id","name")
        return [(x[0],x[1]) for x in qs]
    
    def queryset(self, request, queryset):
        goal = self.value()
        if goal:
            goal = int(goal)
            return queryset.filter(id=goal)|queryset.filter(parent=goal)
        
        return queryset
    
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    model = Goal
    list_display = ["parent","code","name","outcome","kpi"]
    list_filter = [MainGoalFilter,]

class TaskDurationInline(admin.TabularInline):
    model = TaskDuration
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    model = Task
    inlines = [TaskDurationInline]
    list_display = ["name","main_goal","goal","year",]
    list_filter = ["year","responsible__name"]
    search_fields = ('name', 'goal__parent__name','goal__name')
    ordering = ('goal__code',)

    formfield_overrides = {
        models.IntegerField: {"widget": TextInput},
    }    

    @admin.display(description=_('main_goal'))
    def main_goal(self, obj):
        return f'{obj.goal.parent.name}'

@admin.register(TaskAutomation)
class TaskAutomationAdmin(LogAdminMixin,admin.ModelAdmin):
    model = TaskAutomation

class CompanyProductionMonthlyPlanningInline(admin.TabularInline):
    model = CompanyProductionMonthlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class TraditionaProductionMonthlyPlanningInline(admin.TabularInline):
    model = TraditionaProductionMonthlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    
    
class OtherMineralsProductionMonthlyPlanningInline(admin.TabularInline):
    model = OtherMineralsProductionMonthlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class TraditionaTahsilMonthlyPlanningInline(admin.TabularInline):
    model = TraditionaTahsilMonthlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class TraditionaTahsilByBandMonthlyPlanningInline(admin.TabularInline):
    model = TraditionaTahsilByBandMonthlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class TraditionaTahsilByJihaMonthlyPlanningInline(admin.TabularInline):
    model = TraditionaTahsilByJihaMonthlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class ExportGoldTraditionalMonthlyPlanningInline(admin.TabularInline):
    model = ExportGoldTraditionalMonthlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class ExportGoldCompanyMonthlyPlanningInline(admin.TabularInline):
    model = ExportGoldCompanyMonthlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

@admin.register(YearlyPlanning)
class YearlyPlanningAdmin(admin.ModelAdmin):
    model = YearlyPlanning
    list_display = ["year","state",]
    list_filter = ["year","state",]
    inlines = [CompanyProductionMonthlyPlanningInline, TraditionaProductionMonthlyPlanningInline, OtherMineralsProductionMonthlyPlanningInline, TraditionaTahsilMonthlyPlanningInline, TraditionaTahsilByBandMonthlyPlanningInline, TraditionaTahsilByJihaMonthlyPlanningInline, ExportGoldCompanyMonthlyPlanningInline, ExportGoldTraditionalMonthlyPlanningInline, ]

@admin.register(MonthelyReport)
class MonthelyReportAdmin(LogAdminMixin,admin.ModelAdmin):
    model = MonthelyReport
    list_display = ["month","year",]
    list_filter = ["year",]
    search_fields = ('name', 'goal__parent__name','goal__name')
    ordering = ('-year','-month',)

    # inlines = [CompanyProductionTaskInline, TraditionalProductionTaskInline, TraditionalStateTaskInline, OtherMineralsTaskInline, ExportGoldTraditionalTaskInline, ExportGoldCompanyTaskInline, CompanyInfoTaskInline, CompanyLicenseInfoTaskInline]

    formfield_overrides = {
        models.IntegerField: {"widget": TextInput},
    }    

@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    model = TaskExecution
    fields = ["task","percentage","problems"]
    list_display = ["task_name","main_goal","sub_goal","percentage"]
    inlines = []
    readonly_fields = ["task"]

    # readonly_fields = ["task"]
    search_fields = ('task__goal__parent__name','task__goal__name','task__name', 'problems')
    ordering = ('task__goal__code',)

    formfield_overrides = {
        models.IntegerField: {"widget": TextInput},
    }    

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        try:
            qs = qs.filter(task__responsible=request.user.planning_department)

            return qs
        except:
            pass

        return qs.none()

    def has_add_permission(self, request):
        
        return False

    def has_change_permission(self, request, obj=None):
        if obj and request.user.is_superuser:
            if obj.state==STATE_DRAFT:
                return True
        
        try:
            if obj and request.user.planning_department==obj.task.responsible:
                if obj.state==STATE_DRAFT:
                    return super().has_change_permission(request,obj)
        except Exception as e:
            print("User not accepted",e)
        
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            if obj and obj.state==STATE_DRAFT:
                return True
        return False

    @admin.display(description=_('main_goal'))
    def main_goal(self, obj):
        return f'{obj.task.goal.parent}'

    @admin.display(description=_('sub_goal'))
    def sub_goal(self, obj):
        return f'{obj.task.goal}'

    @admin.display(description=_('task'))
    def task_name(self, obj):
        return f'{obj.task.name}'

    def get_inline_instances(self, request, obj=None):
        try:
            return [getattr(sys.modules[__name__],auto.view)(self.model, self.admin_site) for auto in obj.task.automation.all()]
        except Exception as e:
            return []

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)

            if isinstance(inline,CompanyProductionTaskInline):
                formset.form = CompanyProductionTaskForm
                formset.form.company_types = get_company_types(request)

            yield formset,inline
