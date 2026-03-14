import sys
from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _

from planning.forms import DepartmentForm
from planning.utils import get_company_types

from .models import STATE_DRAFT, STATE_CONFIRMED, CompanyProductionQuarterlyPlanning, ExportGoldCompanyQuarterlyPlanning, ExportGoldTraditionalQuarterlyPlanning, Goal, Department, QuarterlyReport, OtherMineralsProductionQuarterlyPlanning, Task, TaskAutomation, TaskDuration, TaskExecution, TraditionaProductionQuarterlyPlanning, TraditionaTahsilByBandQuarterlyPlanning, TraditionaTahsilByJihaQuarterlyPlanning, TraditionaTahsilQuarterlyPlanning, YearlyPlanning

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

class CompanyProductionQuarterlyPlanningInline(admin.TabularInline):
    model = CompanyProductionQuarterlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class TraditionaProductionQuarterlyPlanningInline(admin.TabularInline):
    model = TraditionaProductionQuarterlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    
    
class OtherMineralsProductionQuarterlyPlanningInline(admin.TabularInline):
    model = OtherMineralsProductionQuarterlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class TraditionaTahsilQuarterlyPlanningInline(admin.TabularInline):
    model = TraditionaTahsilQuarterlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class TraditionaTahsilByBandQuarterlyPlanningInline(admin.TabularInline):
    model = TraditionaTahsilByBandQuarterlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class TraditionaTahsilByJihaQuarterlyPlanningInline(admin.TabularInline):
    model = TraditionaTahsilByJihaQuarterlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class ExportGoldTraditionalQuarterlyPlanningInline(admin.TabularInline):
    model = ExportGoldTraditionalQuarterlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class ExportGoldCompanyQuarterlyPlanningInline(admin.TabularInline):
    model = ExportGoldCompanyQuarterlyPlanning
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

@admin.register(YearlyPlanning)
class YearlyPlanningAdmin(LogAdminMixin, admin.ModelAdmin):
    model = YearlyPlanning
    list_display = ["year","state",]
    list_filter = ["year","state",]
    inlines = [CompanyProductionQuarterlyPlanningInline, TraditionaProductionQuarterlyPlanningInline, OtherMineralsProductionQuarterlyPlanningInline, TraditionaTahsilQuarterlyPlanningInline, TraditionaTahsilByBandQuarterlyPlanningInline, TraditionaTahsilByJihaQuarterlyPlanningInline, ExportGoldCompanyQuarterlyPlanningInline, ExportGoldTraditionalQuarterlyPlanningInline, ]

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/reset-draft/',
                self.admin_site.admin_view(self.reset_to_draft),
                name='planning_yearlyplanning_reset_to_draft',
            ),
        ]
        return custom_urls + urls

    def reset_to_draft(self, request, object_id):
        from django.shortcuts import redirect
        from django.urls import reverse
        from django.utils.translation import gettext as _
        
        obj = self.get_object(request, object_id)
        if obj and obj.state == STATE_CONFIRMED:
            obj.state = STATE_DRAFT
            obj.save()
            self.message_user(request, _("تم إرجاع الخطة إلى مسودة بنجاح."))
        return redirect(reverse('admin:planning_yearlyplanning_change', args=[object_id]))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj and obj.state == STATE_CONFIRMED:
            extra_context['is_confirmed'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == STATE_CONFIRMED:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.state == STATE_CONFIRMED:
            return False
        return super().has_delete_permission(request, obj)

@admin.register(QuarterlyReport)
class QuarterlyReportAdmin(LogAdminMixin,admin.ModelAdmin):
    model = QuarterlyReport
    list_display = ["quarter","year",]
    list_filter = ["year",]
    search_fields = ('name', 'goal__parent__name','goal__name')
    ordering = ('-year','-quarter',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.state == STATE_CONFIRMED:
            # When confirmed, we need to populate tasks if they don't already exist.
            # Using get_or_create to prevent duplication if saved multiple times.
            qs = TaskDuration.objects.filter(quarter=obj.quarter, task__year=obj.year)
            for task_duration in qs:
                TaskExecution.objects.get_or_create(
                    report=obj,
                    task=task_duration.task,
                    defaults={
                        'created_by': request.user,
                        'updated_by': request.user,
                        'percentage': 0,
                    }
                )

    # inlines = [CompanyProductionTaskInline, TraditionalProductionTaskInline, TraditionalStateTaskInline, OtherMineralsTaskInline, ExportGoldTraditionalTaskInline, ExportGoldCompanyTaskInline, CompanyInfoTaskInline, CompanyLicenseInfoTaskInline]

    formfield_overrides = {
        models.IntegerField: {"widget": TextInput},
    }

@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    model = TaskExecution
    fields = ["report","task","percentage","problems",]
    list_display = ["task_name","main_goal","sub_goal","percentage"]
    inlines = []
    readonly_fields = ["task","report"]

    # readonly_fields = ["task"]
    search_fields = ('task__goal__parent__name','task__goal__name','task__name', 'problems')
    ordering = ('task__goal__code',)

    formfield_overrides = {
        models.IntegerField: {"widget": TextInput},
    }    

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name__in=["planning_manager",]).exists():
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
            return [getattr(sys.modules[__name__],auto.view)(self.model, self.admin_site) for auto in obj.task.automation.filter(type=TaskAutomation.TYPE_MANUAL)]
        except Exception as e:
            return []

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            yield formset,inline
