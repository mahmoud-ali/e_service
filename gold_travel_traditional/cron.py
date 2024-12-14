from django.utils import timezone
from .models import AppMoveGoldTraditional

def before_three_days():
    return timezone.now() - timezone.timedelta(days=3)

def expired_app():
    for obj in AppMoveGoldTraditional.objects.filter(issue_date__lt=before_three_days):
        obj.state = AppMoveGoldTraditional.STATE_EXPIRED