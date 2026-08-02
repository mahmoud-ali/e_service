from django.db import migrations
from django.utils import timezone

def migrate_existing_dabtiaat(apps, schema_editor):
    AppDabtiaat = apps.get_model('dabtiaat_altaedin', 'AppDabtiaat')
    AppDabtiaatDetails = apps.get_model('dabtiaat_altaedin', 'AppDabtiaatDetails')
    DabtiaatSetting = apps.get_model('dabtiaat_altaedin', 'DabtiaatSetting')
    AppDabtiaatCalculationHistory = apps.get_model('dabtiaat_altaedin', 'AppDabtiaatCalculationHistory')

    all_dabtiaat = AppDabtiaat.objects.all()

    for app in all_dabtiaat:
        # Calculate sum of weight and total price
        details = AppDabtiaatDetails.objects.filter(app_dabtiaat=app)
        weight = sum(d.gold_weight_in_gram or 0.0 for d in details)
        total_val = sum((d.gold_weight_in_gram or 0.0) * (d.gold_price or 0.0) for d in details)

        calc_date = getattr(app, 'created_at', None) or timezone.now()

        # 1. Total Koli calculation
        koli_setting = DabtiaatSetting.objects.filter(key='total_koli_pct').first()
        if koli_setting:
            koli_pct = koli_setting.percentage if koli_setting.is_active else 0.0
            is_active_koli = koli_setting.is_active
        else:
            base_total_qs = DabtiaatSetting.objects.filter(calculation_base='TOTAL').exclude(key='total_koli_pct')
            if base_total_qs.exists():
                koli_pct = sum(s.percentage for s in base_total_qs if s.is_active)
            else:
                koli_pct = 22.0
            is_active_koli = True

        koli_amt = total_val * (koli_pct / 100.0)

        AppDabtiaatCalculationHistory.objects.get_or_create(
            app_dabtiaat=app,
            setting_key='total_koli_pct',
            defaults={
                'calculation_date': calc_date,
                'total_gold_weight': weight,
                'total_gold_value': total_val,
                'setting_name': 'إجمالي الكلي',
                'percentage': koli_pct,
                'calculation_base': 'TOTAL',
                'calculated_amount': koli_amt,
                'is_active': is_active_koli,
            }
        )

        # 2. All settings
        hafiz_setting = DabtiaatSetting.objects.filter(key='alhafiz').first()
        if hafiz_setting and hafiz_setting.is_active:
            hafiz_amt = total_val * (hafiz_setting.percentage / 100.0)
        else:
            hafiz_amt = total_val * 0.10 if not hafiz_setting else 0.0

        settings_qs = DabtiaatSetting.objects.exclude(key='total_koli_pct').order_by('id')
        for setting in settings_qs:
            if not setting.is_active:
                amt = 0.0
            elif setting.calculation_base == 'HAFIZ':
                amt = hafiz_amt * (setting.percentage / 100.0)
            else:
                amt = total_val * (setting.percentage / 100.0)

            AppDabtiaatCalculationHistory.objects.get_or_create(
                app_dabtiaat=app,
                setting_key=setting.key,
                defaults={
                    'calculation_date': calc_date,
                    'total_gold_weight': weight,
                    'total_gold_value': total_val,
                    'setting_name': setting.name,
                    'percentage': setting.percentage,
                    'calculation_base': setting.calculation_base,
                    'calculated_amount': amt,
                    'is_active': setting.is_active,
                }
            )

def reverse_migration(apps, schema_editor):
    AppDabtiaatCalculationHistory = apps.get_model('dabtiaat_altaedin', 'AppDabtiaatCalculationHistory')
    AppDabtiaatCalculationHistory.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('dabtiaat_altaedin', '0020_appdabtiaatcalculationhistory'),
    ]

    operations = [
        migrations.RunPython(migrate_existing_dabtiaat, reverse_migration),
    ]
