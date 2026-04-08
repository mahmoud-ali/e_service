from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_migrate

def create_state_hr_group(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from traditional_app.models import (
        Employee, EmployeeJobData, EmployeeStatus, EmployeeBankAccount,
        EmployeeLeave, EmployeePenalty, EmployeeDocument
    )

    group, created = Group.objects.get_or_create(name='state_hr_traditional')

    models_to_grant = [
        Employee, EmployeeJobData, EmployeeStatus, EmployeeBankAccount,
        EmployeeLeave, EmployeePenalty, EmployeeDocument
    ]
    action_types = ['add', 'change', 'view']
    perms_to_add = []
    
    for model in models_to_grant:
        content_type = ContentType.objects.get_for_model(model)
        for action in action_types:
            codename = f"{action}_{model._meta.model_name}"
            try:
                perm = Permission.objects.get(codename=codename, content_type=content_type)
                perms_to_add.append(perm)
            except Permission.DoesNotExist:
                pass
                
    group.permissions.set(perms_to_add)

class TraditionalAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'traditional_app'
    verbose_name = _("ا.ع لشئون الولايات")

    def ready(self):
        post_migrate.connect(create_state_hr_group, sender=self)
