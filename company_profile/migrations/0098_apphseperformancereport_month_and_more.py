# Generated by Django 5.0.2 on 2025-01-20 11:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0097_alter_appborrowmaterial_borrow_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='apphseperformancereport',
            name='month',
            field=models.PositiveIntegerField(choices=[(1, 'MONTH_JAN'), (2, 'MONTH_FEB'), (3, 'MONTH_MAR'), (4, 'MONTH_APR'), (5, 'MONTH_MAY'), (6, 'MONTH_JUN'), (7, 'MONTH_JLY'), (8, 'MONTH_AUG'), (9, 'MONTH_SEP'), (10, 'MONTH_OCT'), (11, 'MONTH_NOV'), (12, 'MONTH_DEC')], default=1, verbose_name='month'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='apphseperformancereport',
            name='year',
            field=models.PositiveIntegerField(default=2025, validators=[django.core.validators.MinValueValidator(limit_value=2015), django.core.validators.MaxValueValidator(limit_value=2100)], verbose_name='year'),
            preserve_default=False,
        ),
    ]
