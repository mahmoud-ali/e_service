# Generated by Django 5.0.2 on 2024-03-16 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('check_cordinates', '0006_alter_smallmining_license_nu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smallmining',
            name='company_name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
