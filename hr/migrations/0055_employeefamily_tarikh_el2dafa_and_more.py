# Generated by Django 5.0.2 on 2024-08-11 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0054_alter_settings_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeefamily',
            name='tarikh_el2dafa',
            field=models.DateField(blank=True, null=True, verbose_name='tarikh_el2dafa'),
        ),
        migrations.AddField(
            model_name='employeemoahil',
            name='tarikh_el2dafa',
            field=models.DateField(blank=True, null=True, verbose_name='tarikh_el2dafa'),
        ),
        migrations.AlterField(
            model_name='employeebasic',
            name='phone',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='phone'),
        ),
    ]