from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BillingApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'traditional_api'
    verbose_name = _("traditional_api")
