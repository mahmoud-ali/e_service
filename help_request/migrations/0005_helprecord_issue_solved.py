# Generated by Django 5.0.2 on 2024-06-11 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('help_request', '0004_alter_helprecord_options_alter_helprecord_issue_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='helprecord',
            name='issue_solved',
            field=models.BooleanField(default=False, verbose_name='issue_solved'),
        ),
    ]
