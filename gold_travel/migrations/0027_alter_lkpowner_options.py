# Generated by Django 5.1 on 2024-11-17 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel', '0026_appmovegold_owner_name_lst'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lkpowner',
            options={'ordering': ['name'], 'verbose_name': 'owner_name', 'verbose_name_plural': 'owner_name'},
        ),
    ]
