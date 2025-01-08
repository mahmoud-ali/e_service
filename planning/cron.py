from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import TaskDuration, TaskExecution

admin_user = get_user_model().objects.get(id=1)

def generate_tasks():
    current_month,current_year = timezone.now().month,timezone.now().year

    qs = TaskDuration.objects.filter(month=current_month,task__year=current_year)
    
    for obj in qs:
        TaskExecution.objects.get_or_create(
            task=obj.task,
            year=obj.task.year,
            month=obj.month,
            percentage=0,
            created_by=admin_user,
            updated_by=admin_user,
        )