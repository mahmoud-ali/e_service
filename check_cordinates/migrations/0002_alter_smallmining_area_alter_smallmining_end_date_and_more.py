# Generated by Django 5.0.2 on 2024-03-16 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('check_cordinates', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smallmining',
            name='area',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='smallmining',
            name='end_date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='smallmining',
            name='mineral',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='smallmining',
            name='nots',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='smallmining',
            name='state',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='smallmining',
            name='valid',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]