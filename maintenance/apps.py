from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MaintenanceConfig(AppConfig):
    default_auto_field  = 'django.db.models.BigAutoField'
    name                = 'maintenance'
    verbose_name        = _('نظام الصيانة')

    def ready(self):
        import maintenance.signals  # noqa: F401
