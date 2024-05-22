from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

class DocWorkflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doc_workflow'

    verbose_name = _("Executive workflow")

    def ready(self) -> None:
        #register & call signals
        from .models import ApplicationDepartmentProcessing,ApplicationExectiveProcessing,ApplicationDelivery
        from . import signals

        post_save.connect(
            signals.update_application_record_state_from_department_processing,
            sender=ApplicationDepartmentProcessing, 
            dispatch_uid="update_application_record_from_department_processing_signal_id",
        )

        post_save.connect(
            signals.update_application_record_state_from_executive_processing,
            sender=ApplicationExectiveProcessing, 
            dispatch_uid="update_application_record_state_from_executive_processing_signal_id",
        )

        post_save.connect(
            signals.update_application_record_state_from_delivery_ready,
            sender=ApplicationDelivery, 
            dispatch_uid="update_application_record_state_from_delivery_ready_signal_id",
        )

        return super().ready()
    
