from django.db import migrations
from django.contrib.auth.management import create_permissions
from django.apps import apps as global_apps


def create_kimyaeya_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Force Django to create permissions for 'mokhalafat'
    try:
        app_config = global_apps.get_app_config('mokhalafat')
        create_permissions(app_config, verbosity=0)
    except Exception:
        pass

    chemical_models = [
        'appchemicalmaterialsviolation',
        'appchemicalmaterialsviolationitem',
        'appchemicalmaterialsviolationwitness',
        'appchemicalmaterialsviolationattachment',
    ]

    def get_permissions(action_list, model_names):
        perms = []
        for model_name in model_names:
            try:
                ct = ContentType.objects.get(app_label='mokhalafat', model=model_name)
                for action in action_list:
                    codename = f'{action}_{model_name}'
                    try:
                        perm = Permission.objects.get(content_type=ct, codename=codename)
                        perms.append(perm)
                    except Permission.DoesNotExist:
                        pass
            except ContentType.DoesNotExist:
                pass
        return perms

    state_group, _ = Group.objects.get_or_create(name='mokhalafat_kimyaeya_state')
    state_perms = get_permissions(['view', 'add', 'change', 'delete'], chemical_models)
    if state_perms:
        state_group.permissions.set(state_perms)

    manager_group, _ = Group.objects.get_or_create(name='mokhalafat_kimyaeya_manager')
    manager_perms = get_permissions(['view', 'change'], chemical_models)
    if manager_perms:
        manager_group.permissions.set(manager_perms)


def remove_kimyaeya_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(
        name__in=['mokhalafat_kimyaeya_state', 'mokhalafat_kimyaeya_manager']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mokhalafat', '0008_add_record_state_source_state_to_chemical_violation'),
    ]

    operations = [
        migrations.RunPython(create_kimyaeya_groups, remove_kimyaeya_groups),
    ]
