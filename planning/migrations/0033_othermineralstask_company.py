# Generated by Django 5.0.2 on 2025-01-13 11:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0084_alter_appborrowmaterial_company_from_str'),
        ('planning', '0032_remove_othermineralstask_mineral_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='othermineralstask',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='company_profile.tblcompanyproduction', verbose_name='company'),
            preserve_default=False,
        ),
    ]
