from django.utils import timezone
from .models import AppMoveGoldTraditional

def expired_app():
    before_three_days = (timezone.now() - timezone.timedelta(days=3)).date()

    AppMoveGoldTraditional.objects\
        .filter(state__in=[AppMoveGoldTraditional.STATE_NEW,],issue_date__lt=before_three_days)\
        .update(state=AppMoveGoldTraditional.STATE_EXPIRED)
    
    AppMoveGoldTraditional.objects\
        .filter(state__in=[AppMoveGoldTraditional.STATE_RENEW,],renew_date__lt=before_three_days)\
        .update(state=AppMoveGoldTraditional.STATE_EXPIRED)
    