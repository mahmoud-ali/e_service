from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _

from .models import STATE_DRAFT, Goal, Department, Task, TaskDuration, TaskExecution

class LogAdminMixin:
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

        return False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    list_display = ["user","name"]

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    model = Goal
    list_display = ["parent","code","name","outcome","kpi"]
    # list_filter = ["state","has_2lestikhbarat_2l3askria"]

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
    list_filter = ["year","responsible"]
    search_fields = ('name', 'goal__parent__name','goal__name')
    ordering = ('goal__code',)

    formfield_overrides = {
        models.IntegerField: {"widget": TextInput},
    }    

    @admin.display(description=_('main_goal'))
    def main_goal(self, obj):
        return f'{obj.goal.parent.name}'

@admin.register(TaskExecution)
class TaskExecutionAdmin(LogAdminMixin,admin.ModelAdmin):
    model = TaskExecution
    fields = ["percentage","problems"]
    list_display = ["main_goal","sub_goal","task","percentage"]
    readonly_fields = ["task"]
    search_fields = ('task__goal__parent__name','task__goal__name','task__name', 'problems')
    ordering = ('task__goal__code',)

    formfield_overrides = {
        models.IntegerField: {"widget": TextInput},
    }    

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        try:
            qs = qs.filter(task__responsible=request.user.planning_department)

            return qs
        except:
            pass

        return qs.none()
    
    @admin.display(description=_('main_goal'))
    def main_goal(self, obj):
        return f'{obj.task.goal.parent}'

    @admin.display(description=_('sub_goal'))
    def sub_goal(self, obj):
        return f'{obj.task.goal}'
