from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

class ExecutiveOfficeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'executive_office'
    verbose_name = _("Executive Office")

    def ready(self) -> None:
        #register & call signals
        from .models import Inbox,InboxTasks
        from . import signals

        post_save.connect(signals.add_tasks_from_template,sender=Inbox, dispatch_uid="add_tasks_from_template_signal_id")
        post_save.connect(signals.update_inbox_state,sender=InboxTasks, dispatch_uid="update_inbox_state_signal_id")
