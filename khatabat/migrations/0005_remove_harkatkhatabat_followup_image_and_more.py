# Generated by Django 5.1.7 on 2025-05-12 10:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khatabat', '0004_alter_khatabat_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='harkatkhatabat',
            name='followup_image',
        ),
        migrations.RemoveField(
            model_name='harkatkhatabat',
            name='letter_image',
        ),
        migrations.RemoveField(
            model_name='harkatkhatabat',
            name='notes',
        ),
        migrations.AddField(
            model_name='harkatkhatabat',
            name='followup_attachment',
            field=models.FileField(blank=True, null=True, upload_to='mutabaah/', verbose_name='صورة نتيجة المتابعة'),
        ),
        migrations.AddField(
            model_name='harkatkhatabat',
            name='letter_attachment',
            field=models.FileField(default='', upload_to='khatabat/', verbose_name='صورة الخطاب'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='harkatkhatabat',
            name='procedure',
            field=models.TextField(default='', verbose_name='الإجراء'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='harkatkhatabat',
            name='receive_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='تاريخ الاستلام'),
            preserve_default=False,
        ),
    ]
