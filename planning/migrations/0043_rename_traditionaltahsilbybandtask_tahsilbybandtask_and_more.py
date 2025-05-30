# Generated by Django 5.0.2 on 2025-01-16 12:41

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0042_exportgoldcompanymonthlyplanning_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TraditionalTahsilByBandTask',
            new_name='TahsilByBandTask',
        ),
        migrations.RenameModel(
            old_name='TraditionalTahsilByJihaTask',
            new_name='TahsilByJihaTask',
        ),
        migrations.AlterModelOptions(
            name='tahsilbybandtask',
            options={'verbose_name': 'TahsilByBandTask', 'verbose_name_plural': 'TahsilByBandTasks'},
        ),
        migrations.AlterModelOptions(
            name='tahsilbyjihatask',
            options={'verbose_name': 'TahsilByJihaTask', 'verbose_name_plural': 'TahsilByJihaTasks'},
        ),
        migrations.AddField(
            model_name='taskexecution',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='created_at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskexecution',
            name='created_by',
            field=models.ForeignKey(default=1, editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskexecution',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='updated_at'),
        ),
        migrations.AddField(
            model_name='taskexecution',
            name='updated_by',
            field=models.ForeignKey(default=1, editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by'),
            preserve_default=False,
        ),
    ]
