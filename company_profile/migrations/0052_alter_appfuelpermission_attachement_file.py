# Generated by Django 5.0.2 on 2024-03-19 14:40

import company_profile.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0051_remove_appexportgold_f2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appfuelpermission',
            name='attachement_file',
            field=models.FileField(upload_to=company_profile.models.company_applications_path, verbose_name='fuel_request_file'),
        ),
    ]