# Generated by Django 5.0.2 on 2024-06-11 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0067_alter_tblcompanyproduction_manager_phone_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tblcompanyproduction',
            name='nationality',
        ),
        migrations.AddField(
            model_name='tblcompanyproduction',
            name='nationality',
            field=models.ManyToManyField(to='company_profile.lkpnationality', verbose_name='nationality'),
        ),
    ]
