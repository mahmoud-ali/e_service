# Generated by Django 5.0.2 on 2024-08-22 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0074_alter_tblcompanyproduction_nationality_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tblcompanyproductionlicense',
            name='business_profit',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Business profit'),
        ),
        migrations.AddField(
            model_name='tblcompanyproductionlicense',
            name='social_responsibility',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Social responsibility'),
        ),
    ]