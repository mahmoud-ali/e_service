# Generated by Django 5.0.1 on 2024-02-07 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0036_apprequirementslist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apprequirementslistchemicalequipments',
            name='description',
            field=models.TextField(max_length=256, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='apprequirementslistchemicallabequipments',
            name='description',
            field=models.TextField(max_length=256, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='apprequirementslistelectricityequipments',
            name='description',
            field=models.TextField(max_length=256, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='apprequirementslistfactoryequipments',
            name='description',
            field=models.TextField(max_length=256, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='apprequirementslistmangamequipments',
            name='description',
            field=models.TextField(max_length=256, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='apprequirementslistmotafjeratequipments',
            name='description',
            field=models.TextField(max_length=256, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='apprequirementslistvehiclesequipments',
            name='description',
            field=models.TextField(max_length=256, verbose_name='description'),
        ),
    ]
