# Generated by Django 5.1.7 on 2025-04-21 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hse_companies', '0002_alter_apphseperformancereport_state_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='apphseperformancereportauditorcomment',
            options={'verbose_name': 'ملاحظات المراقب', 'verbose_name_plural': 'ملاحظات المراقب'},
        ),
    ]
