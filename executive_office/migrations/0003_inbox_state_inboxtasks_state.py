# Generated by Django 5.0.2 on 2024-12-30 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('executive_office', '0002_alter_senderentity_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox',
            name='state',
            field=models.IntegerField(choices=[(1, 'state_draft'), (2, 'state_processing'), (3, 'state_done')], default=1, verbose_name='record_state'),
        ),
        migrations.AddField(
            model_name='inboxtasks',
            name='state',
            field=models.IntegerField(choices=[(1, 'state_draft'), (2, 'state_processing'), (3, 'state_done')], default=1, verbose_name='record_state'),
        ),
    ]
