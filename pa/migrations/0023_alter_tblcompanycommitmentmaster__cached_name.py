# Generated by Django 5.2.1 on 2025-06-29 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pa', '0022_tblcompanycommitmentmaster__cached_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblcompanycommitmentmaster',
            name='_cached_name',
            field=models.CharField(blank=True, default='', max_length=150, null=True),
        ),
    ]
