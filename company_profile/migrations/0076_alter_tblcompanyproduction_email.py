# Generated by Django 5.0.2 on 2024-09-02 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0075_tblcompanyproductionlicense_business_profit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblcompanyproduction',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=100, null=True, verbose_name='Official email'),
        ),
    ]
