# Generated by Django 5.0.2 on 2025-02-21 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sswg', '0006_alter_cbsdata_basic_form_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='basicform',
            name='state',
            field=models.IntegerField(choices=[(1, 'SSWG State 1'), (2, 'SSWG State 2'), (3, 'SSWG State 3'), (4, 'SSWG State 4'), (5, 'SSWG State 5'), (6, 'SSWG State 6'), (7, 'SSWG State 7'), (8, 'SSWG State 8'), (9, 'SSWG State 9'), (10, 'SSWG State 10')], default=1, verbose_name='record_state'),
        ),
    ]
