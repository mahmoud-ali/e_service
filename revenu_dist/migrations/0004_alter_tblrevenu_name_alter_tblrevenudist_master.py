# Generated by Django 5.0.2 on 2024-09-03 09:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revenu_dist', '0003_alter_tblrevenu_options_alter_tblrevenudist_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblrevenu',
            name='name',
            field=models.CharField(max_length=100, verbose_name='note'),
        ),
        migrations.AlterField(
            model_name='tblrevenudist',
            name='master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='revenu_dist.tblrevenu'),
        ),
    ]