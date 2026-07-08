from django.utils import timezone
from .models import AppMoveGoldTraditional

def expired_app():
    today = timezone.now().date()

    for record in AppMoveGoldTraditional.objects.filter(
        state__in=[AppMoveGoldTraditional.STATE_NEW]
    ):
        expiry_date = record.issue_date + timezone.timedelta(days=record.expiry_days)
        if today >= expiry_date:
            record.state = AppMoveGoldTraditional.STATE_EXPIRED
            record.save(update_fields=['state'])

    for record in AppMoveGoldTraditional.objects.filter(
        state__in=[AppMoveGoldTraditional.STATE_RENEW]
    ):
        if record.renew_date:
            expiry_date = record.renew_date + timezone.timedelta(days=record.expiry_days)
            if today >= expiry_date:
                record.state = AppMoveGoldTraditional.STATE_EXPIRED
                record.save(update_fields=['state'])