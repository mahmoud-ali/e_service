from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

class ProductionControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'production_control'
    verbose_name = _("production_control")
