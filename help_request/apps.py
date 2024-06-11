from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HelpRequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'help_request'
    verbose_name = _('help request')
