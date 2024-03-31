from django.apps import AppConfig
from django.db.models.signals import post_save

class PaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pa'

    def ready(self) -> None:
        #register & call signals
        from .models import TblCompanyCommitment,TblCompanyRequest,TblCompanyPayment
        from . import signals

        post_save.connect(signals.commitement_generate_request,sender=TblCompanyCommitment, dispatch_uid="commitement_generate_request_signal_id")
        post_save.connect(signals.send_email_after_add_request,sender=TblCompanyRequest, dispatch_uid="request_send_email_after_add_request_signal_id")
        post_save.connect(signals.update_request_payment_state,sender=TblCompanyPayment, dispatch_uid="payment_update_request_payment_state_signal_id")

        return super().ready()
    
