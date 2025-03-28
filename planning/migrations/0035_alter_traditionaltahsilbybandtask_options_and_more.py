# Generated by Django 5.0.2 on 2025-01-13 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0034_alter_companyinfotask_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='traditionaltahsilbybandtask',
            options={'verbose_name': 'TraditionalTahsilByBandTask', 'verbose_name_plural': 'TraditionalTahsilByBandTasks'},
        ),
        migrations.CreateModel(
            name='TraditionalTahsilByJihaTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jiha', models.IntegerField(choices=[(1, 'jiha_1'), (2, 'jiha_2'), (3, 'jiha_3'), (4, 'jiha_4'), (5, 'jiha_5')], verbose_name='jiha')),
                ('total_money', models.FloatField(verbose_name='total_money')),
                ('task_execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='planning.taskexecution', verbose_name='task_execution')),
            ],
            options={
                'verbose_name': 'TraditionalTahsilByJihaTask',
                'verbose_name_plural': 'TraditionalTahsilByJihaTasks',
            },
        ),
    ]
