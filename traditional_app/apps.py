from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_migrate

def setup_hr_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from traditional_app.models import (
        Employee, EmployeeJobData, EmployeeStatus, EmployeeBankAccount,
        EmployeeLeave, EmployeePenalty, EmployeeDocument, AcademicQualification,
        PayrollMaster, PayrollDetail, EmployeeCategory
    )

    # Models only for central HR (including salaries)
    central_hr_models = [
        Employee, EmployeeJobData, EmployeeStatus, EmployeeBankAccount,
        EmployeeLeave, EmployeePenalty, EmployeeDocument, AcademicQualification,
        PayrollMaster, PayrollDetail, EmployeeCategory
    ]
    
    # Models for state HR (excluding salaries)
    state_hr_models = [
        Employee, EmployeeJobData, EmployeeStatus, EmployeeBankAccount,
        EmployeeLeave, EmployeePenalty, EmployeeDocument, AcademicQualification,
        EmployeeCategory
    ]
    
    groups_config = {
        'traditional_hr': {
            'models': central_hr_models,
            'actions': ['add', 'change', 'view', 'delete']
        },
        'state_hr_traditional': {
            'models': state_hr_models,
            'actions': ['add', 'change', 'view']
        },
    }
    
    for group_name, config in groups_config.items():
        group, created = Group.objects.get_or_create(name=group_name)
        perms_to_add = []
        
        for model in config['models']:
            content_type = ContentType.objects.get_for_model(model)
            for action in config['actions']:
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
        post_migrate.connect(setup_hr_groups, sender=self)
