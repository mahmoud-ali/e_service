from django.db import migrations

def setup_group_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    fleet_content_types = ContentType.objects.filter(app_label='fleet')
    fleet_permissions = Permission.objects.filter(content_type__in=fleet_content_types)

    hr_content_types = ContentType.objects.filter(app_label='hr')
    hr_view_permissions = Permission.objects.filter(content_type__in=hr_content_types, codename__startswith='view_')

    group_names = ['fleet_manager', 'fleet_employee']

    for name in group_names:
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.add(*fleet_permissions)
        group.permissions.add(*hr_view_permissions)



def reverse_group_permissions(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0045_remove_fuelbeneficiarysetting_default_amount_and_more'),
    ]

    operations = [
        migrations.RunPython(setup_group_permissions, reverse_code=reverse_group_permissions),
    ]
