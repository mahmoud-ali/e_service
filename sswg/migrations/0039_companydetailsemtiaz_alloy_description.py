# Generated by Django 5.2.1 on 2025-06-02 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sswg', '0038_productioncompany_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='companydetailsemtiaz',
            name='alloy_description',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='وصف السبائك'),
        ),
    ]
