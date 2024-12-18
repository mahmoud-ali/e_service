# Generated by Django 5.1 on 2024-11-07 09:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0080_tblcompanyproductionlicense_area_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tblcompanyproduction',
            options={'ordering': ['name_ar'], 'verbose_name': 'Production Company', 'verbose_name_plural': 'Production Companies'},
        ),
        migrations.AlterModelOptions(
            name='tblcompanyproductionlicense',
            options={'ordering': ['-date'], 'verbose_name': 'Production Company License', 'verbose_name_plural': 'Production Company Licenses'},
        ),
        migrations.AddIndex(
            model_name='tblcompanyproduction',
            index=models.Index(fields=['code'], name='company_pro_code_911f98_idx'),
        ),
        migrations.AddIndex(
            model_name='tblcompanyproduction',
            index=models.Index(fields=['email'], name='company_pro_email_552239_idx'),
        ),
        migrations.AddIndex(
            model_name='tblcompanyproduction',
            index=models.Index(fields=['status'], name='company_pro_status__5aaf03_idx'),
        ),
        migrations.AddIndex(
            model_name='tblcompanyproductionlicense',
            index=models.Index(fields=['date'], name='company_pro_date_4a70ff_idx'),
        ),
        migrations.AddIndex(
            model_name='tblcompanyproductionlicense',
            index=models.Index(fields=['contract_status'], name='company_pro_contrac_d7c6c0_idx'),
        ),
    ]
