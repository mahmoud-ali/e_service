# Generated by Django 5.0.2 on 2024-05-24 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0007_alter_employeebasic_moahil_alter_settings_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edara3ama',
            name='name',
            field=models.CharField(max_length=150, verbose_name='edara_3ama'),
        ),
        migrations.AlterField(
            model_name='edarafar3ia',
            name='name',
            field=models.CharField(max_length=150, verbose_name='edara_far3ia'),
        ),
    ]