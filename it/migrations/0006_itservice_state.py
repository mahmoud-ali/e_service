# Generated by Django 5.0.2 on 2025-03-05 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it', '0005_itservice_itservicemodification_itserviceoperation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='itservice',
            name='state',
            field=models.IntegerField(choices=[(1, 'draft'), (2, 'confirmed')], default=1, verbose_name='record_state'),
        ),
    ]
