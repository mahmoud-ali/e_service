# Generated by Django 5.0.2 on 2024-05-02 17:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0064_lkpaccidenttype_apphseaccidentreport_accident_class_and_more'),
        ('pa', '0013_remove_tblcompanyopenningbalancedetail_amount_factor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tblcompanycommitmentmaster',
            name='license',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='company_profile.tblcompanyproductionlicense', verbose_name='license'),
        ),
    ]
