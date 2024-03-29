# Generated by Django 5.0.2 on 2024-03-20 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0053_alter_appvisibitystudydetail_study_point_lat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appworkplan',
            name='plan_comments',
            field=models.TextField(default='', max_length=256, verbose_name='plan_comments'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='apptajeeltnazol',
            name='tnazol_type',
            field=models.CharField(choices=[('first', 'first'), ('second', 'fourth')], max_length=15, verbose_name='tnazol_type'),
        ),
    ]
