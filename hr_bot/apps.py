from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class HrBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr_bot'
    verbose_name = _("HR portal")
