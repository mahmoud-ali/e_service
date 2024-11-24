from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

class ProductionControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'production_control'
    verbose_name = _("production_control")

    def ready(self) -> None:
        #register & call signals
        from .models import GoldShippingForm
        from . import signals

        post_save.connect(signals.alloy_shipped,sender=GoldShippingForm, dispatch_uid="gold_shipping_form_alloy_shipped_signal_id")

        return super().ready()
