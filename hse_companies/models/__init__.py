from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpState
from .performance_report import *
from .incidents import *
from .corrective_actions import *

class TblStateRepresentative(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="hse_cmpny_state",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, related_name="hse_cmpny_state",verbose_name=_("state"))

    def __str__(self):
        return f'{self.user} ({self.state.name})'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'state'], name='hse_cmpny_unique_user_state')
        ]

        verbose_name = _("state representative")
        verbose_name_plural = _("state representatives")
