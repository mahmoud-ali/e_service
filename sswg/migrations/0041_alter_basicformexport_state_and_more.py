# Generated by Django 5.2.1 on 2025-06-24 12:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sswg', '0040_companydetailsemtiaz_travel_cert_no'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='basicformexport',
            name='state',
            field=models.IntegerField(choices=[(1, 'SSWG State 1'), (2, 'SSWG State 2'), (3, 'SSWG State 3'), (4, 'SSWG State 4'), (5, 'SSWG State 5'), (6, 'SSWG State 6'), (7, 'SSWG State 7'), (8, 'SSWG State 8'), (9, 'SSWG State 9'), (10, 'SSWG State 10'), (11, 'SSWG State 11'), (12, 'SSWG State 12'), (13, 'SSWG State 13'), (14, 'SSWG State 14')], default=1, verbose_name='record_state'),
        ),
        migrations.AlterField(
            model_name='basicformexportcompany',
            name='state',
            field=models.IntegerField(choices=[(1, 'SSWG State 1'), (2, 'SSWG State 2'), (3, 'SSWG State 3'), (4, 'SSWG State 4'), (5, 'SSWG State 5'), (6, 'SSWG State 6'), (7, 'SSWG State 7'), (8, 'SSWG State 8'), (9, 'SSWG State 9'), (10, 'SSWG State 10'), (11, 'SSWG State 11'), (12, 'SSWG State 12'), (13, 'SSWG State 13'), (14, 'SSWG State 14')], default=1, verbose_name='record_state'),
        ),
        migrations.AlterField(
            model_name='basicformreexport',
            name='state',
            field=models.IntegerField(choices=[(1, 'SSWG State 1'), (2, 'SSWG State 2'), (3, 'SSWG State 3'), (4, 'SSWG State 4'), (5, 'SSWG State 5'), (6, 'SSWG State 6'), (7, 'SSWG State 7'), (8, 'SSWG State 8'), (9, 'SSWG State 9'), (10, 'SSWG State 10'), (11, 'SSWG State 11'), (12, 'SSWG State 12'), (13, 'SSWG State 13'), (14, 'SSWG State 14')], default=1, verbose_name='record_state'),
        ),
        migrations.AlterField(
            model_name='basicformsilver',
            name='state',
            field=models.IntegerField(choices=[(1, 'SSWG State 1'), (2, 'SSWG State 2'), (3, 'SSWG State 3'), (4, 'SSWG State 4'), (5, 'SSWG State 5'), (6, 'SSWG State 6'), (7, 'SSWG State 7'), (8, 'SSWG State 8'), (9, 'SSWG State 9'), (10, 'SSWG State 10'), (11, 'SSWG State 11'), (12, 'SSWG State 12'), (13, 'SSWG State 13'), (14, 'SSWG State 14')], default=1, verbose_name='record_state'),
        ),
        migrations.CreateModel(
            name='CustomForceAirportData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('comment', models.TextField(verbose_name='إفادة ضابط الجمارك بمنفذ الصادر')),
                ('basic_form_export', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cfa_data_export', to='sswg.basicformexport', verbose_name='SSWG Basic Form')),
                ('basic_form_export_emtiaz', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cfa_data_export_emtiaz', to='sswg.basicformexportcompany', verbose_name='SSWG Basic Form')),
                ('basic_form_reexport', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cfa_data_reexport', to='sswg.basicformreexport', verbose_name='SSWG Basic Form')),
                ('basic_form_silver', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cfa_data_silver', to='sswg.basicformsilver', verbose_name='SSWG Basic Form')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
            ],
            options={
                'verbose_name': 'قوة الجمارك بمنفذ الصادر',
                'verbose_name_plural': 'قوة الجمارك بمنفذ الصادر',
            },
        ),
        migrations.CreateModel(
            name='UnifiedTeamData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('airline_name', models.CharField(max_length=150, verbose_name='عبر طيران')),
                ('flight_number', models.CharField(max_length=50, verbose_name='رقم الرحلة')),
                ('flight_datetime', models.DateTimeField(verbose_name='زمن الرحلة')),
                ('destination', models.CharField(max_length=150, verbose_name='جهة الرحلة')),
                ('basic_form_export', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='unified_team_data_export', to='sswg.basicformexport', verbose_name='SSWG Basic Form')),
                ('basic_form_export_emtiaz', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='unified_team_data_export_emtiaz', to='sswg.basicformexportcompany', verbose_name='SSWG Basic Form')),
                ('basic_form_reexport', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='unified_team_data_reexport', to='sswg.basicformreexport', verbose_name='SSWG Basic Form')),
                ('basic_form_silver', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='unified_team_data_silver', to='sswg.basicformsilver', verbose_name='SSWG Basic Form')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
            ],
            options={
                'verbose_name': 'فريق الترحيل الموحد',
                'verbose_name_plural': 'فريق الترحيل الموحد',
            },
        ),
    ]
