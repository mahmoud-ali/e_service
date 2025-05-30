# Generated by Django 5.0.2 on 2025-02-17 08:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0115_alter_apphseperformancereportchemicalused_expire_dt'),
        ('planning', '0043_rename_traditionaltahsilbybandtask_tahsilbybandtask_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GMTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, 'gm_task_1'), (2, 'gm_task_2'), (3, 'gm_task_3'), (4, 'gm_task_4'), (5, 'gm_task_5'), (6, 'gm_task_6'), (7, 'gm_task_7')], verbose_name='type')),
                ('count', models.IntegerField(verbose_name='count')),
                ('comments', models.TextField(verbose_name='comments')),
                ('task_execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='planning.taskexecution', verbose_name='task_execution')),
            ],
            options={
                'verbose_name': 'GMTask',
                'verbose_name_plural': 'GMTasks',
            },
        ),
        migrations.CreateModel(
            name='Mas2oliaMojtama3iaTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locality', models.CharField(max_length=50, verbose_name='locality')),
                ('amount', models.FloatField(verbose_name='amount')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='company_profile.lkpstate', verbose_name='state')),
                ('task_execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='planning.taskexecution', verbose_name='task_execution')),
            ],
            options={
                'verbose_name': 'Mas2oliaMojtama3iaTask',
                'verbose_name_plural': 'Mas2oliaMojtama3iaTasks',
            },
        ),
        migrations.CreateModel(
            name='MediaDiscoveryTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, 'no3_discovery_1'), (2, 'no3_discovery_2'), (3, 'no3_discovery_3'), (4, 'no3_discovery_4'), (5, 'no3_discovery_5')], verbose_name='type')),
                ('count', models.IntegerField(verbose_name='count')),
                ('task_execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='planning.taskexecution', verbose_name='task_execution')),
            ],
            options={
                'verbose_name': 'MediaDiscoveryTask',
                'verbose_name_plural': 'MediaDiscoveryTasks',
            },
        ),
        migrations.CreateModel(
            name='MediaF2atMostakhdmaTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, 'no3_media_mostathmir_1'), (2, 'no3_media_mostathmir_2'), (3, 'no3_media_mostathmir_3'), (4, 'no3_media_mostathmir_4'), (5, 'no3_media_mostathmir_5')], verbose_name='type')),
                ('count', models.IntegerField(verbose_name='count')),
                ('task_execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='planning.taskexecution', verbose_name='task_execution')),
            ],
            options={
                'verbose_name': 'MediaF2atMostakhdmaTask',
                'verbose_name_plural': 'MediaF2atMostakhdmaTasks',
            },
        ),
        migrations.CreateModel(
            name='MediaITSupportTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, 'no3_it_support_1'), (2, 'no3_it_support_2'), (3, 'no3_it_support_3'), (4, 'no3_it_support_4'), (5, 'no3_it_support_5'), (6, 'no3_it_support_6'), (7, 'no3_it_support_7'), (8, 'no3_it_support_8'), (9, 'no3_it_support_9'), (10, 'no3_it_support_10')], verbose_name='type')),
                ('count', models.IntegerField(verbose_name='count')),
                ('task_execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='planning.taskexecution', verbose_name='task_execution')),
            ],
            options={
                'verbose_name': 'MediaITSupportTask',
                'verbose_name_plural': 'MediaITSupportTasks',
            },
        ),
        migrations.CreateModel(
            name='MediaRasdBathTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no3_bath', models.IntegerField(choices=[(1, 'no3_bath_1'), (2, 'no3_bath_2'), (3, 'no3_bath_3')], verbose_name='no3_bath')),
                ('count', models.IntegerField(verbose_name='count')),
                ('count_positive', models.IntegerField(verbose_name='count_positive')),
                ('task_execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='planning.taskexecution', verbose_name='task_execution')),
            ],
            options={
                'verbose_name': 'MediaRasdBathTask',
                'verbose_name_plural': 'MediaRasdBathTasks',
            },
        ),
    ]
