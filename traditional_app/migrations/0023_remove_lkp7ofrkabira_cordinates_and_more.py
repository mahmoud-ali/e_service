# Generated by Django 5.1.7 on 2025-05-13 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traditional_app', '0022_lkplocalitytmp_locality_lkplocalitytmp_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lkp7ofrkabira',
            name='cordinates',
        ),
        migrations.AddField(
            model_name='lkp7ofrkabira',
            name='cordinates_x',
            field=models.FloatField(default=0, verbose_name='الإحداثيات x'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lkp7ofrkabira',
            name='cordinates_y',
            field=models.FloatField(default=0, verbose_name='الإحداثيات y'),
            preserve_default=False,
        ),
    ]
