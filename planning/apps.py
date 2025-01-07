from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class PlanningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'planning'
    verbose_name = _("Planning app")
