# Generated by Django 5.1.7 on 2025-03-25 11:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0117_lkpsector_lkpstate_sector'),
        ('production_control', '0026_alter_goldproductionform_company_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GoldProductionSectorUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('company_type', models.CharField(choices=[('entaj', 'entaj'), ('mokhalfat', 'mokhalfat'), ('emtiaz', 'emtiaz'), ('sageer', 'sageer')], max_length=15, verbose_name='company_type')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('sector', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='company_profile.lkpsector', verbose_name='sector')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='gold_production_sector_user', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'مشرف القطاع',
                'verbose_name_plural': 'مشرفي القطاعات',
            },
        ),
        migrations.CreateModel(
            name='GoldProductionStateUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('company_type', models.CharField(choices=[('entaj', 'entaj'), ('mokhalfat', 'mokhalfat'), ('emtiaz', 'emtiaz'), ('sageer', 'sageer')], max_length=15, verbose_name='company_type')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='company_profile.lkpstate', verbose_name='state')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='gold_production_state_user', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'رئيس القسم بالولاية',
                'verbose_name_plural': 'رؤساء الاقسام بالولايات',
            },
        ),
    ]
