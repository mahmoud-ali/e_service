from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from gold_travel_traditional.models import (
    GoldTravelTraditionalUser,
    GoldTravelTraditionalUserJihatAlaisdar,
    GoldTravelTraditionalUserJihatTarhil,
    Route,
)


def sync_user_destinations(user):
    """
    Sync GoldTravelTraditionalUserJihatTarhil entries for a single user
    based on their assigned jihat_alaisdar × Route definitions.

    Only applies to user_type=1 (pure issuer) users.
    """
    if user.user_type != GoldTravelTraditionalUser.JIHAT_ALAISDAR:
        return

    issuer_ids = user.goldtraveltraditionaluserjihatalaisdar_set.values_list(
        'jihat_alaisdar_id', flat=True
    )
    route_dest_ids = set(
        Route.objects.filter(jihat_alaisdar_id__in=issuer_ids).values_list(
            'wijhat_altarhil_id', flat=True
        )
    )

    existing_dest_ids = set(
        user.goldtraveltraditionaluserjihattarhil_set.values_list(
            'wijhat_altarhil_id', flat=True
        )
    )

    # Add missing destinations
    for dest_id in route_dest_ids - existing_dest_ids:
        GoldTravelTraditionalUserJihatTarhil.objects.create(
            master=user, wijhat_altarhil_id=dest_id, can_arrive=False
        )

    # Remove stale destinations (no longer in any route)
    user.goldtraveltraditionaluserjihattarhil_set.exclude(
        wijhat_altarhil_id__in=route_dest_ids
    ).delete()


def sync_all_issuer_users():
    """Sync destinations for all pure-issuer (user_type=1) users."""
    for user in GoldTravelTraditionalUser.objects.filter(
        user_type=GoldTravelTraditionalUser.JIHAT_ALAISDAR
    ):
        sync_user_destinations(user)


@receiver(post_save, sender=Route)
@receiver(post_delete, sender=Route)
def on_route_changed(sender, instance, **kwargs):
    sync_all_issuer_users()


@receiver(post_save, sender=GoldTravelTraditionalUserJihatAlaisdar)
@receiver(post_delete, sender=GoldTravelTraditionalUserJihatAlaisdar)
def on_user_jihat_alaisdar_changed(sender, instance, **kwargs):
    sync_user_destinations(instance.master)
