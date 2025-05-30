# Generated by Django 5.0.2 on 2025-03-06 14:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hse_traditional', '0006_hsetraditionalcorrectiveaction'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='achievement',
            options={'verbose_name': 'Achievement', 'verbose_name_plural': 'Achievements'},
        ),
        migrations.AlterModelOptions(
            name='arrangementofmarkets',
            options={'verbose_name': 'Arrangement Of Market', 'verbose_name_plural': 'Arrangement Of Markets'},
        ),
        migrations.AlterModelOptions(
            name='environmentalinspection',
            options={'verbose_name': 'Environmental Inspection', 'verbose_name_plural': 'Environmental Inspections'},
        ),
        migrations.AlterModelOptions(
            name='environmentalrequirements',
            options={'verbose_name': 'Environmental Requirement', 'verbose_name_plural': 'Environmental Requirements'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalaccident',
            options={'verbose_name': 'Hse Traditional Accident', 'verbose_name_plural': 'Hse Traditional Accidents'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalaccidentdamage',
            options={'verbose_name': 'Hse Traditional Accident damage', 'verbose_name_plural': 'Hse Traditional Accident damages'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalaccidentinjury',
            options={'verbose_name': 'Hse Traditional Accident injury', 'verbose_name_plural': 'Hse Traditional Accident injuries'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalaccidentwho',
            options={'verbose_name': 'Hse Traditional Accident Who', 'verbose_name_plural': 'Hse Traditional Accident Whos'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalaccidentwhy',
            options={'verbose_name': 'Hse Traditional Accident Why', 'verbose_name_plural': 'Hse Traditional Accident Whys'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalcorrectiveaction',
            options={'verbose_name': 'Hse Traditional Corrective Action', 'verbose_name_plural': 'Hse Traditional Corrective Action'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalnearmiss',
            options={'verbose_name': 'Hse Traditional Near Miss', 'verbose_name_plural': 'Hse Traditional Near Miss'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalnearmisswho',
            options={'verbose_name': 'Hse Traditional Near Miss Who', 'verbose_name_plural': 'Hse Traditional Near Miss Whos'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalnearmisswhy',
            options={'verbose_name': 'Hse Traditional Near Miss why', 'verbose_name_plural': 'Hse Traditional Near Miss whys'},
        ),
        migrations.AlterModelOptions(
            name='hsetraditionalreport',
            options={'verbose_name': 'Hse Traditional Monthly Report', 'verbose_name_plural': 'Hse Traditional Monthly Reports'},
        ),
        migrations.AlterModelOptions(
            name='quickemergencyteam',
            options={'verbose_name': 'Quick Emergency Team', 'verbose_name_plural': 'Quick Emergency Teams'},
        ),
        migrations.AlterModelOptions(
            name='trainingawareness',
            options={'verbose_name': 'Training Awareness', 'verbose_name_plural': 'Training Awareness'},
        ),
        migrations.AlterModelOptions(
            name='wastemanagement',
            options={'verbose_name': 'Waste Management', 'verbose_name_plural': 'Waste Managements'},
        ),
        migrations.AlterField(
            model_name='hsetraditionalreport',
            name='month',
            field=models.IntegerField(choices=[(1, 'MONTH_JAN'), (2, 'MONTH_FEB'), (3, 'MONTH_MAR'), (4, 'MONTH_APR'), (5, 'MONTH_MAY'), (6, 'MONTH_JUN'), (7, 'MONTH_JLY'), (8, 'MONTH_AUG'), (9, 'MONTH_SEP'), (10, 'MONTH_OCT'), (11, 'MONTH_NOV'), (12, 'MONTH_DEC')], verbose_name='month'),
        ),
        migrations.CreateModel(
            name='HseTraditionalCorrectiveActionFinalDecision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='description')),
                ('action', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='corrective_action_final_decision', to='hse_traditional.hsetraditionalcorrectiveaction')),
            ],
            options={
                'verbose_name': 'Hse Traditional Corrective Action Final Decision',
                'verbose_name_plural': 'Hse Traditional Corrective Action Final Decisions',
            },
        ),
        migrations.CreateModel(
            name='HseTraditionalCorrectiveActionReccomendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='description')),
                ('action', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='corrective_action_reccomendation', to='hse_traditional.hsetraditionalcorrectiveaction')),
            ],
            options={
                'verbose_name': 'Hse Traditional Corrective Action Reccomendation',
                'verbose_name_plural': 'Hse Traditional Corrective Action Reccomendations',
            },
        ),
    ]
