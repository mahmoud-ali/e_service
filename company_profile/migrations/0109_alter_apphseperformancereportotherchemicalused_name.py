# Generated by Django 5.0.2 on 2025-01-23 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0108_alter_apphseperformancereportotherchemicalused_expire_dt_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apphseperformancereportotherchemicalused',
            name='name',
            field=models.CharField(default='not exists', max_length=100, verbose_name='hse_chemical_used'),
        ),
    ]
