# Generated by Django 5.0.2 on 2024-10-06 14:54

import pa.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pa', '0017_alter_tblcompanycommitmentdetail_commitment_master_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tblcompanypaymentdetail',
            name='attachement_file',
        ),
        migrations.RemoveField(
            model_name='tblcompanyrequestdetail',
            name='attachement_file',
        ),
        migrations.AddField(
            model_name='tblcompanypaymentmaster',
            name='attachement_file',
            field=models.FileField(blank=True, upload_to=pa.models.TblCompanyPaymentMaster.attachement_path2, verbose_name='attachement_file'),
        ),
        migrations.AddField(
            model_name='tblcompanyrequestmaster',
            name='attachement_file',
            field=models.FileField(blank=True, upload_to=pa.models.TblCompanyRequestMaster.attachement_path, verbose_name='attachement_file'),
        ),
        migrations.AddField(
            model_name='tblcompanyrequestmaster',
            name='note',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='note'),
        ),
    ]
