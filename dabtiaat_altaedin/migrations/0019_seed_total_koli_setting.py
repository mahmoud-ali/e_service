from django.db import migrations

def seed_total_koli(apps, schema_editor):
    DabtiaatSetting = apps.get_model('dabtiaat_altaedin', 'DabtiaatSetting')
    DabtiaatSetting.objects.get_or_create(
        key='total_koli_pct',
        defaults={
            'name': 'إجمالي نسبة الكلي',
            'percentage': 22.0,
            'calculation_base': 'TOTAL',
            'is_active': True
        }
    )

def unseed_total_koli(apps, schema_editor):
    DabtiaatSetting = apps.get_model('dabtiaat_altaedin', 'DabtiaatSetting')
    DabtiaatSetting.objects.filter(key='total_koli_pct').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('dabtiaat_altaedin', '0018_seed_dabtiaat_settings'),
    ]

    operations = [
        migrations.RunPython(seed_total_koli, unseed_total_koli),
    ]
