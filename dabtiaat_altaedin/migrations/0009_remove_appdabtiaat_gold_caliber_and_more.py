# Generated by Django 5.1.7 on 2025-04-26 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dabtiaat_altaedin', '0008_appdabtiaatdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appdabtiaat',
            name='gold_caliber',
        ),
        migrations.RemoveField(
            model_name='appdabtiaat',
            name='gold_price',
        ),
        migrations.RemoveField(
            model_name='appdabtiaat',
            name='gold_weight_in_gram',
        ),
    ]
