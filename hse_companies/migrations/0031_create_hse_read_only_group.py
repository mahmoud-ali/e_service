from django.db import migrations

def create_hse_readonly_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    group_name = 'hse_read_only'
    group, created = Group.objects.get_or_create(name=group_name)
    
    hse_apps = ['hse_companies', 'hse_traditional']
    
    permissions_to_add = []
    
    all_cts = ContentType.objects.filter(app_label__in=hse_apps)
    for ct in all_cts:
        codename = f'view_{ct.model}'
        try:
            perm = Permission.objects.get(content_type=ct, codename=codename)
            permissions_to_add.append(perm)
        except Permission.DoesNotExist:
            pass

    cp_cts = ContentType.objects.filter(app_label='company_profile', model__startswith='apphse')
    for ct in cp_cts:
        codename = f'view_{ct.model}'
        try:
            perm = Permission.objects.get(content_type=ct, codename=codename)
            permissions_to_add.append(perm)
        except Permission.DoesNotExist:
            pass
            
    if permissions_to_add:
        group.permissions.set(permissions_to_add)

def remove_hse_readonly_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='hse_read_only').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('hse_companies', '0030_remove_apphsecorrectiveaction_company_and_more'),
        ('auth', '__first__'),
        ('contenttypes', '__first__'),
    ]
    operations = [
        migrations.RunPython(create_hse_readonly_group, remove_hse_readonly_group),
    ]
