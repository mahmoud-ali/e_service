# Generated by Django 5.0.2 on 2025-01-19 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0089_apphseperformancereportworkenvironment'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppHSEPerformanceReportProactiveIndicators',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factor', models.PositiveIntegerField(choices=[(1, 'proactive_indicators_type1'), (2, 'proactive_indicators_type2'), (3, 'proactive_indicators_type3'), (4, 'proactive_indicators_type4')], verbose_name='proactive_indicators')),
                ('no_gov', models.PositiveIntegerField(verbose_name='no_gov')),
                ('no_staff', models.PositiveIntegerField(verbose_name='no_staff')),
                ('no_contractor', models.PositiveIntegerField(verbose_name='no_contractor')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='company_profile.apphseperformancereport')),
            ],
            options={
                'verbose_name': 'HSE proactive indicators',
                'verbose_name_plural': 'HSE proactive indicators',
            },
        ),
    ]
