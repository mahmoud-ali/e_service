from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class GoldTravelTraditionalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gold_travel_traditional'
    verbose_name = _("Gold travel Traditional")

    def ready(self) -> None:

        return super().ready()
    
