# Generated by Django 5.1 on 2024-11-28 09:11

import production_control.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production_control', '0013_alter_goldproductionformalloy_master_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goldshippingform',
            name='attachement_file',
            field=models.FileField(blank=True, null=True, upload_to=production_control.models.company_applications_path, verbose_name='gold_shipping_form_file'),
        ),
    ]
