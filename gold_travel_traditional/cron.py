from django.utils import timezone
from .models import AppMoveGoldTraditional, GoldTravelTraditionalState
from company_profile.models import LkpState

def expired_app():
    today = timezone.now().date()

    for state in LkpState.objects.all():
        config = GoldTravelTraditionalState.objects.filter(state=state).first()
        expiry_days = config.expiry_days if config else 3

        expiry_date = today - timezone.timedelta(days=expiry_days)

        AppMoveGoldTraditional.objects.filter(
            source_state=state,
            state=AppMoveGoldTraditional.STATE_NEW,
            issue_date__lt=expiry_date
        ).update(state=AppMoveGoldTraditional.STATE_EXPIRED)

        AppMoveGoldTraditional.objects.filter(
            source_state=state,
            state=AppMoveGoldTraditional.STATE_RENEW,
            renew_date__lt=expiry_date
        ).update(state=AppMoveGoldTraditional.STATE_EXPIRED)