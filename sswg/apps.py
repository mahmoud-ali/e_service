from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SswgConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sswg'
    verbose_name = _("SSWG App")
    # description = _("This app manages the SSWG functionalities.")
