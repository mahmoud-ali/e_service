# Generated by Django 5.0.2 on 2024-12-31 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('executive_office', '0013_inboxcompany'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inboxtasks',
            name='title',
            field=models.CharField(max_length=200, verbose_name='task_title'),
        ),
    ]