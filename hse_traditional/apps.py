from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class HseTraditionalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hse_traditional'
    verbose_name = _("hse traditional")
