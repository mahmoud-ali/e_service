from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _

from .models import Goal, Department, Task, TaskDuration, TaskExecution

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    list_display = ["user","name"]

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    model = Goal
    list_display = ["parent","code","name","outcome","kpi","responsible"]
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
    list_display = ["main_goal","goal","year","name"]
    list_filter = ["year"]
    search_fields = ('name', 'goal__parent__name','goal__name')

    formfield_overrides = {
        models.IntegerField: {"widget": TextInput},
    }    

    @admin.display(description=_('main_goal'))
    def main_goal(self, obj):
        return f'{obj.goal.parent.name}'

@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    model = TaskExecution
    list_display = ["main_goal","sub_goal","task","percentage"]
    search_fields = ('task__goal__parent__name','task__goal__name','task__name', 'problems')

    @admin.display(description=_('main_goal'))
    def main_goal(self, obj):
        return f'{obj.task.goal.parent}'

    @admin.display(description=_('sub_goal'))
    def sub_goal(self, obj):
        return f'{obj.task.goal}'
