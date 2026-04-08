
from django.db import migrations

def assign_hr_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    model_names = [
        'employee', 
        'employeejobdata', 
        'employeestatus', 
        'employeebankaccount',
        'employeeleave', 
        'employeepenalty', 
        'employeedocument', 
        'academicqualification'
    ]
    
    try:
        group, created = Group.objects.get_or_create(name='traditional_hr')
        
        for model_name in model_names:
            try:
                content_type = ContentType.objects.get(app_label='traditional_app', model=model_name)
                permissions = Permission.objects.filter(content_type=content_type)
                for perm in permissions:
                    group.permissions.add(perm)
            except ContentType.DoesNotExist:
                continue
    except Exception:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('traditional_app', '0048_delete_employeesalary'),
    ]

    operations = [
        migrations.RunPython(assign_hr_permissions),
    ]
