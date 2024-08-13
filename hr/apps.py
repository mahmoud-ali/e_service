from django.apps import AppConfig
from django.db.models.signals import post_save,post_delete
from django.utils.translation import gettext_lazy as _

class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'
    verbose_name = _("human resource")

    def ready(self) -> None:
        #register & call signals
        from .models import EmployeeBankAccount,EmployeeFamily,EmployeeMoahil,Edarafar3ia
        from . import signals

        post_save.connect(signals.one_active_employee_bank_account,sender=EmployeeBankAccount, dispatch_uid="one_active_employee_bank_account_signal_id")
        post_save.connect(signals.update_employee_social_data,sender=EmployeeFamily, dispatch_uid="update_employee_social_data_signal_id")
        post_save.connect(signals.update_employee_moahil,sender=EmployeeMoahil, dispatch_uid="update_employee_moahil_signal_id")

        post_delete.connect(signals.delete_one_active_employee_bank_account,sender=EmployeeBankAccount, dispatch_uid="delete_one_active_employee_bank_account_signal_id")
        post_delete.connect(signals.delete_update_employee_social_data,sender=EmployeeFamily, dispatch_uid="delete_update_employee_social_data_signal_id")
        post_delete.connect(signals.delete_update_employee_moahil,sender=EmployeeMoahil, dispatch_uid="delete_update_employee_moahil_signal_id")

        post_save.connect(signals.update_edara_far3ia,sender=Edarafar3ia, dispatch_uid="update_edara_far3ia_signal_id")

        return super().ready()
