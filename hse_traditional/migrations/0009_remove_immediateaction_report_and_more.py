# Generated by Django 5.0.2 on 2025-03-09 08:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hse_traditional', '0008_immediateaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='immediateaction',
            name='report',
        ),
        migrations.AddField(
            model_name='immediateaction',
            name='accident',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='immediate_actions', to='hse_traditional.hsetraditionalaccident'),
            preserve_default=False,
        ),
    ]
