# Generated by Django 5.0.2 on 2025-03-17 13:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traditional_app', '0007_remove_lkpmojam3attawa7in_attachment_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GoldMor7ala',
            new_name='DailyGoldMor7ala',
        ),
        migrations.RenameModel(
            old_name='KartaMor7ala',
            new_name='DailyKartaMor7ala',
        ),
        migrations.RenameModel(
            old_name='TahsilForm',
            new_name='DailyTahsilForm',
        ),
        migrations.RenameModel(
            old_name='WardHajr',
            new_name='DailyWardHajr',
        ),
        migrations.CreateModel(
            name='DailyGrabeel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('weight_in_gram', models.FloatField(verbose_name='weight_in_gram')),
                ('amount', models.FloatField(verbose_name='amount')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('daily_report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='traditional_app.dailyreport', verbose_name='daily_report')),
                ('grabeel', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='traditional_app.lkpgrabeel', verbose_name='grabeel')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
            ],
            options={
                'verbose_name': 'Grabeel',
                'verbose_name_plural': 'Grabeels',
            },
        ),
        migrations.CreateModel(
            name='DailyHofrKabira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('weight_in_gram', models.FloatField(verbose_name='weight_in_gram')),
                ('amount', models.FloatField(verbose_name='amount')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('daily_report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='traditional_app.dailyreport', verbose_name='daily_report')),
                ('hofr_kabira', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='traditional_app.lkp7ofrkabira', verbose_name='7ofr_kabira')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
            ],
            options={
                'verbose_name': 'Hofr Kabira',
                'verbose_name_plural': 'Hofr Kabiras',
            },
        ),
        migrations.CreateModel(
            name='DailySmallProcessingUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('weight_in_gram', models.FloatField(verbose_name='weight_in_gram')),
                ('amount', models.FloatField(verbose_name='amount')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('daily_report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='traditional_app.dailyreport', verbose_name='daily_report')),
                ('small_processing_unit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='traditional_app.lkpsmallprocessingunit', verbose_name='small_processing_unit')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
            ],
            options={
                'verbose_name': 'Small Processing Unit',
                'verbose_name_plural': 'Small Processing Units',
            },
        ),
    ]
