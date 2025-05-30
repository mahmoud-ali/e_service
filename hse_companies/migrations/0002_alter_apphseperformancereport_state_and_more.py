# Generated by Django 5.1.7 on 2025-04-21 14:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hse_companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apphseperformancereport',
            name='state',
            field=models.IntegerField(choices=[(1, 'draft'), (2, 'مؤكد من المشرف'), (3, 'معتمد من مشرف الولاية')], default=1, verbose_name='record_state'),
        ),
        migrations.CreateModel(
            name='AppHSEPerformanceReportAuditorComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(verbose_name='comment')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hse_companies.apphseperformancereport')),
            ],
        ),
    ]
