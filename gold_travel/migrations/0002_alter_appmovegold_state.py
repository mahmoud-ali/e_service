# Generated by Django 5.0.2 on 2024-10-17 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appmovegold',
            name='state',
            field=models.IntegerField(choices=[(1, 'state_draft'), (2, 'state_smrc'), (3, 'state_2mn_2lm3adin'), (4, 'state_shortat_2lm3adin'), (5, 'state_2lestikhbarat_2l3askria')], default=1, verbose_name='record_state'),
        ),
    ]