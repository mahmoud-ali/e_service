# Generated by Django 5.0.1 on 2024-02-06 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0028_appforeignerproceduredetail'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appforeignerprocedure',
            options={'ordering': ['-id'], 'verbose_name': 'Application: Foreigner procedure', 'verbose_name_plural': 'Application: Foreigner procedure'},
        ),
    ]