# Generated by Django 5.0.2 on 2024-03-22 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0060_appgoldproduction_appgoldproductiondetail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appgoldproductiondetail',
            name='melt_added_gold',
            field=models.FloatField(blank=True, verbose_name='melt_added_gold'),
        ),
        migrations.AlterField(
            model_name='appgoldproductiondetail',
            name='melt_dt',
            field=models.DateField(verbose_name='melt_dt'),
        ),
        migrations.AlterField(
            model_name='appgoldproductiondetail',
            name='melt_remaind',
            field=models.FloatField(blank=True, verbose_name='melt_remaind'),
        ),
    ]