# Generated by Django 5.0.2 on 2025-02-13 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dabtiaat_altaedin', '0003_delete_lkpstatedetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appdabtiaat',
            name='state',
            field=models.IntegerField(choices=[(1, 'state_draft'), (2, 'state_smrc'), (8, 'state_canceled')], default=1, verbose_name='record_state'),
        ),
    ]
