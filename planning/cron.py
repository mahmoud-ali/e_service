from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import QuarterlyReport, TaskDuration, TaskExecution

admin_user = get_user_model().objects.get(id=1)

def generate_tasks():
    # Note: Logic to determine the current quarter
    current_month = timezone.now().month
    current_quarter = (current_month - 1) // 3 + 1
    current_year = timezone.now().year

    quarter_rep,_ = QuarterlyReport.objects.get_or_create(
        year=current_year,
        quarter=current_quarter,
        created_by=admin_user,
        updated_by=admin_user,
    )

    TaskExecution.objects.filter(report=quarter_rep).delete()

    qs = TaskDuration.objects.filter(quarter=current_quarter,task__year=current_year)
    
    for obj in qs:
        TaskExecution.objects.create(
            report=quarter_rep,
            task=obj.task,
            percentage=0,
            created_by=admin_user,
            updated_by=admin_user,
        )