# Generated by Django 5.0.2 on 2025-01-28 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0111_alter_apphseperformancereportbillsofquantities_factor'),
    ]

    operations = [
        migrations.AddField(
            model_name='apphseperformancereport',
            name='note',
            field=models.TextField(blank=True, null=True, verbose_name='note'),
        ),
    ]
