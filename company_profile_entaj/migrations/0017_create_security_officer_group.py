from django.db import migrations

def create_security_officer_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    group, _ = Group.objects.get_or_create(name='security_officer')

    target_models = [
        ('company_profile_entaj', 'foreignerrecord'),
        ('company_profile_entaj', 'foreignerpermission'),
        ('company_profile_entaj', 'foreignerprocedure'),
        ('company_profile', 'appforignermovement'),
    ]

    perms_to_add = []
    for app_label, model_name in target_models:
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
            for action in ['change', 'view']:
                codename = f'{action}_{model_name}'
                perm = Permission.objects.filter(content_type=ct, codename=codename).first()
                if perm:
                    perms_to_add.append(perm)
        except Exception:
            pass

    if perms_to_add:
        group.permissions.add(*perms_to_add)

def remove_security_officer_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='security_officer').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('company_profile_entaj', '0016_security_comment_foreigner'),
        ('auth', '__first__'),
        ('contenttypes', '__first__'),
    ]

    operations = [
        migrations.RunPython(create_security_officer_group, remove_security_officer_group),
    ]
