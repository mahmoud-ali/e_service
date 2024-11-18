from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MokhalafatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mokhalafat'
    verbose_name = _("mokhalafat app")
