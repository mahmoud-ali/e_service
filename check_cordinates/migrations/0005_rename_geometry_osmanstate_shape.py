# Generated by Django 5.1.7 on 2025-04-16 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('check_cordinates', '0004_rename_polygon_osmanstate_geometry'),
    ]

    operations = [
        migrations.RenameField(
            model_name='osmanstate',
            old_name='geometry',
            new_name='shape',
        ),
    ]
