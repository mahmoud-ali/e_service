# Generated by Django 5.0.2 on 2024-05-24 19:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0004_settings'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='settings',
            constraint=models.UniqueConstraint(fields=('code',), name='unique_setting_code'),
        ),
    ]