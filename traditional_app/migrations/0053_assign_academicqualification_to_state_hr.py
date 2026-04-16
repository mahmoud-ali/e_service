from django.db import migrations

def assign_hr_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
def assign_hr_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Models list
    common_models = [
        'employee', 'employeejobdata', 'employeestatus', 'employeebankaccount',
        'employeeleave', 'employeepenalty', 'employeedocument', 'academicqualification',
        'employeecategory'
    ]
    payroll_models = ['payrollmaster', 'payrolldetail']
    
    groups_config = {
        'traditional_hr': {
            'models': common_models + payroll_models,
            'actions': ['add', 'change', 'view', 'delete']
        },
        'state_hr_traditional': {
            'models': common_models,
            'actions': ['add', 'change', 'view']
        },
    }
    
    for group_name, config in groups_config.items():
        try:
            group, created = Group.objects.get_or_create(name=group_name)
            
            # For data migrations, it's safer to clear or carefully add
            # But here we want to ensure the final state
            for model_name in (common_models + payroll_models):
                try:
                    content_type = ContentType.objects.get(app_label='traditional_app', model=model_name)
                    
                    # If model is in group's config, add permissions
                    if model_name in config['models']:
                        for action in config['actions']:
                            codename = f"{action}_{model_name}"
                            perm = Permission.objects.filter(codename=codename, content_type=content_type).first()
                            if perm:
                                group.permissions.add(perm)
                    else:
                        # Otherwise remove them (specifically for payroll for state_hr)
                        for action in ['add', 'change', 'delete', 'view']:
                            codename = f"{action}_{model_name}"
                            perm = Permission.objects.filter(codename=codename, content_type=content_type).first()
                            if perm:
                                group.permissions.remove(perm)
                                
                except ContentType.DoesNotExist:
                    continue
        except Exception:
            pass

class Migration(migrations.Migration):

    dependencies = [
        ('traditional_app', '0052_remove_employee_state_serial_number_and_more'),
    ]

    operations = [
        migrations.RunPython(assign_hr_permissions, reverse_code=migrations.RunPython.noop),
    ]
