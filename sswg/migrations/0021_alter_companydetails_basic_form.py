# Generated by Django 5.1.7 on 2025-05-25 11:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sswg', '0020_alter_companydetails_basic_form'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companydetails',
            name='basic_form',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='company_details', to='sswg.basicform', verbose_name='SSWG Basic Form'),
        ),
    ]
