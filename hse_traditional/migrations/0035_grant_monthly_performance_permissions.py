from django.db import migrations


def grant_monthly_performance_permissions(apps, schema_editor):
    """
    منح الصلاحيات اللازمة لمجموعات موظفي البيئة والسلامة في التعدين التقليدي
    على نماذج تقرير الأداء الشهري — تُطبق تلقائياً مع كل نشر.
    """
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # النماذج التي نحتاج منح صلاحيات عليها
    model_names = [
        'monthlyperformancereport',
        'monthlyperformancehserequirements',
        'monthlyperformanceadmincontrol',
        'monthlyperformancemission',
        'monthlyperformanceobstacle',
    ]

    # المجموعات وصلاحياتها
    group_perms = {
        'hse_tra_state_employee': ['add', 'change', 'delete', 'view'],
        'hse_tra_manager':        ['view'],
        'hse_tra_gm':             ['view'],
        'hse_read_only':          ['view'],
    }

    for group_name, actions in group_perms.items():
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue

        for model_name in model_names:
            try:
                ct = ContentType.objects.get(
                    app_label='hse_traditional',
                    model=model_name,
                )
            except ContentType.DoesNotExist:
                continue

            for action in actions:
                codename = f'{action}_{model_name}'
                try:
                    perm = Permission.objects.get(
                        content_type=ct,
                        codename=codename,
                    )
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    pass


def revoke_monthly_performance_permissions(apps, schema_editor):
    """إلغاء الصلاحيات عند التراجع عن الـ migration"""
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    model_names = [
        'monthlyperformancereport',
        'monthlyperformancehserequirements',
        'monthlyperformanceadmincontrol',
        'monthlyperformancemission',
        'monthlyperformanceobstacle',
    ]

    group_names = ['hse_tra_state_employee', 'hse_tra_manager', 'hse_tra_gm', 'hse_read_only']

    for group_name in group_names:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue

        for model_name in model_names:
            try:
                ct = ContentType.objects.get(
                    app_label='hse_traditional',
                    model=model_name,
                )
                perms = Permission.objects.filter(content_type=ct)
                group.permissions.remove(*perms)
            except ContentType.DoesNotExist:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('hse_traditional', '0034_remove_monthlyperformanceadmincontrol_awareness_meetings_planned_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(
            grant_monthly_performance_permissions,
            revoke_monthly_performance_permissions,
        ),
    ]
