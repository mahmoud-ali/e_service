# Generated by Django 5.0.2 on 2024-05-02 21:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0064_lkpaccidenttype_apphseaccidentreport_accident_class_and_more'),
        ('pa', '0014_tblcompanycommitmentmaster_license'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblcompanycommitmentmaster',
            name='license',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='company_profile.tblcompanyproductionlicense', verbose_name='license'),
        ),
    ]