from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'
    verbose_name = _("human resource")

    def ready(self) -> None:
        #register & call signals
        from .models import EmployeeBankAccount
        from . import signals

        post_save.connect(signals.one_active_employee_bank_account,sender=EmployeeBankAccount, dispatch_uid="one_active_employee_bank_account_signal_id")

        return super().ready()
