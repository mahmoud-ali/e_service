# Generated by Django 5.1.7 on 2025-05-06 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dabtiaat_altaedin', '0013_alter_appdabtiaatdetails_gold_caliber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appdabtiaat',
            name='report_number',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='Report number'),
        ),
        migrations.AlterField(
            model_name='appdabtiaatdetails',
            name='alloy_id',
            field=models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='alloy_id'),
        ),
    ]
