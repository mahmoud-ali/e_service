# Generated by Django 5.0.2 on 2025-02-21 18:51

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel', '0038_alter_lkpstatedetails_reexport_next_serial_no_and_more'),
        ('sswg', '0008_alter_cbsdata_basic_form_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SMRCData',
            new_name='TransferRelocationFormData',
        ),
    ]
