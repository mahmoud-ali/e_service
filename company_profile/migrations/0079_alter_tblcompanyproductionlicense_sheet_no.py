# Generated by Django 5.0.2 on 2024-10-08 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0078_tblcompanyproductionlicense_license_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblcompanyproductionlicense',
            name='sheet_no',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='sheet_no'),
        ),
    ]
