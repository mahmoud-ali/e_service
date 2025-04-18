# Generated by Django 5.0.2 on 2025-03-17 11:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0116_appfuelpermissiondetail_fuel_actual_qty'),
        ('traditional_app', '0002_lkpsoag_locality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lkpsoag',
            name='locality',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='company_profile.lkplocality', verbose_name='Locality'),
        ),
    ]
