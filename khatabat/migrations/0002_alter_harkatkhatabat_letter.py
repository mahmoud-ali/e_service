# Generated by Django 5.1.7 on 2025-05-12 10:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khatabat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harkatkhatabat',
            name='letter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='khatabat.khatabat', verbose_name='رقم الخطاب'),
        ),
    ]
