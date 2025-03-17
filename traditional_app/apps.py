from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TraditionalAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'traditional_app'
    verbose_name = _("ا.ع للتعدين التقليدي")
