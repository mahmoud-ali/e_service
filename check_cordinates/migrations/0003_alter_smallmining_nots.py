# Generated by Django 5.0.2 on 2024-03-16 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('check_cordinates', '0002_alter_smallmining_area_alter_smallmining_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smallmining',
            name='nots',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]