from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import MonthelyReport, TaskDuration, TaskExecution

admin_user = get_user_model().objects.get(id=1)

def generate_tasks():
    current_month,current_year = timezone.now().month,timezone.now().year

    month_rep,_ = MonthelyReport.objects.get_or_create(
        year=current_year,
        month=current_month,
        created_by=admin_user,
        updated_by=admin_user,
    )

    TaskExecution.objects.filter(report=month_rep).delete()

    qs = TaskDuration.objects.filter(month=current_month,task__year=current_year)
    
    for obj in qs:
        TaskExecution.objects.create(
            report=month_rep,
            task=obj.task,
            percentage=0,
            created_by=admin_user,
            updated_by=admin_user,
        )