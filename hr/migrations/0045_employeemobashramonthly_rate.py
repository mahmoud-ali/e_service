# Generated by Django 5.0.2 on 2024-06-03 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0044_employeemobashramonthly_no_days_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeemobashramonthly',
            name='rate',
            field=models.FloatField(default=0, verbose_name='rate'),
            preserve_default=False,
        ),
    ]