from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class RevenuDistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'revenu_dist'
    verbose_name = _("Revenu distiribution")
