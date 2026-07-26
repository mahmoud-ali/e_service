from django.db import migrations

def seed_settings(apps, schema_editor):
    DabtiaatSetting = apps.get_model('dabtiaat_altaedin', 'DabtiaatSetting')

    defaults = [
        {'name': 'العوائد الجليلة', 'key': 'al3wayid_aljalila', 'percentage': 10.0, 'calculation_base': 'TOTAL'},
        {'name': 'الحافز', 'key': 'alhafiz', 'percentage': 10.0, 'calculation_base': 'TOTAL'},
        {'name': 'النيابة', 'key': 'alniyaba', 'percentage': 2.0, 'calculation_base': 'TOTAL'},
        {'name': 'الشركة السودانية M3', 'key': 'smrc', 'percentage': 10.0, 'calculation_base': 'HAFIZ'},
        {'name': 'الولاية', 'key': 'state', 'percentage': 10.0, 'calculation_base': 'HAFIZ'},
        {'name': 'الشرطة', 'key': 'police', 'percentage': 10.0, 'calculation_base': 'HAFIZ'},
        {'name': 'الأمن', 'key': 'amn', 'percentage': 10.0, 'calculation_base': 'HAFIZ'},
        {'name': 'رئاسة القوات الضابطة', 'key': 'riasat_alquat_aldaabita', 'percentage': 10.0, 'calculation_base': 'HAFIZ'},
        {'name': 'القوات الضابطة', 'key': 'alquat_aldaabita', 'percentage': 50.0, 'calculation_base': 'HAFIZ'},
    ]

    for item in defaults:
        DabtiaatSetting.objects.get_or_create(
            key=item['key'],
            defaults=item
        )

def unseed_settings(apps, schema_editor):
    DabtiaatSetting = apps.get_model('dabtiaat_altaedin', 'DabtiaatSetting')
    keys = ['al3wayid_aljalila', 'alhafiz', 'alniyaba', 'smrc', 'state', 'police', 'amn', 'riasat_alquat_aldaabita', 'alquat_aldaabita']
    DabtiaatSetting.objects.filter(key__in=keys).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('dabtiaat_altaedin', '0017_dabtiaatsetting'),
    ]

    operations = [
        migrations.RunPython(seed_settings, unseed_settings),
    ]
