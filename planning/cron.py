from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import MonthelyReport, TaskDuration, TaskExecution

admin_user = get_user_model().objects.get(id=1)

def generate_tasks():
    current_month,current_year = timezone.now().month,timezone.now().year

    qs = TaskDuration.objects.filter(month=current_month,task__year=current_year)
    
    for obj in qs:
        month_rep = MonthelyReport.get_or_create(
            year=obj.task.year,
            month=obj.month,
            created_by=admin_user,
            updated_by=admin_user,
        )

        TaskExecution.objects.get_or_create(
            report=month_rep,
            task=obj.task,
            percentage=0,
            created_by=admin_user,
            updated_by=admin_user,
        )