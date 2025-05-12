from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SandogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sandog'
    verbose_name = _("صندوق العاملين")
