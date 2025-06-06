# Generated by Django 5.0.2 on 2025-03-23 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0116_appfuelpermissiondetail_fuel_actual_qty'),
        ('company_profile_exploration', '0003_alter_targetcommodity_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='TblCompanyExploration',
            fields=[
            ],
            options={
                'verbose_name': 'Production Company',
                'verbose_name_plural': 'Production Companies',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('company_profile.tblcompanyproduction',),
        ),
    ]
