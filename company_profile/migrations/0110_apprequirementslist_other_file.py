# Generated by Django 5.0.2 on 2025-01-26 07:05

import company_profile.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0109_alter_apphseperformancereportotherchemicalused_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='apprequirementslist',
            name='other_file',
            field=models.FileField(blank=True, upload_to=company_profile.models.company_applications_path, verbose_name='other_file'),
        ),
    ]
