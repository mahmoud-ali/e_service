# Generated by Django 5.0.2 on 2025-02-11 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel', '0035_alter_apppreparegold_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='appmovegold',
            name='form_type',
            field=models.IntegerField(choices=[(1, 'form_type_gold_export'), (2, 'form_type_gold_reexport'), (3, 'form_type_silver_export')], default=1, verbose_name='form_type'),
        ),
    ]
