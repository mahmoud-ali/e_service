# Generated by Django 5.0.2 on 2024-10-17 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel', '0009_apppreparegold_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='tblstaterepresentative',
            name='name',
            field=models.CharField(default='', max_length=100, verbose_name='name'),
            preserve_default=False,
        ),
    ]