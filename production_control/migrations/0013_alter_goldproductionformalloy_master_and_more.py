# Generated by Django 5.1 on 2024-11-26 10:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production_control', '0012_rename_attachement_file_goldproductionform_gold_production_form_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goldproductionformalloy',
            name='master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='production_control.goldproductionform'),
        ),
        migrations.AlterField(
            model_name='goldshippingformalloy',
            name='master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='production_control.goldshippingform'),
        ),
    ]
