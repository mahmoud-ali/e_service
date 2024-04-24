from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

class PaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pa'
    verbose_name = _("Production Accounting")

    def ready(self) -> None:
        #register & call signals
        from .models import TblCompanyCommitmentSchedular,TblCompanyRequestMaster,TblCompanyPaymentMaster
        from . import signals

        post_save.connect(signals.commitment_generate_request,sender=TblCompanyCommitmentSchedular, dispatch_uid="commitment_generate_request_signal_id")
        post_save.connect(signals.send_email_after_add_request,sender=TblCompanyRequestMaster, dispatch_uid="request_send_email_after_add_request_signal_id")
        post_save.connect(signals.update_request_payment_state,sender=TblCompanyPaymentMaster, dispatch_uid="payment_update_request_payment_state_signal_id")

        return super().ready()
    
