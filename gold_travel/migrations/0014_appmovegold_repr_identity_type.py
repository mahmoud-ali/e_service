# Generated by Django 5.0.2 on 2024-10-21 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel', '0013_lkpstatedetails_appmovegold_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appmovegold',
            name='repr_identity_type',
            field=models.CharField(choices=[(1, 'identity_passport'), (2, 'identity_personal'), (3, 'identity_national_id')], default=1, max_length=2, verbose_name='repr_identity_type'),
        ),
    ]