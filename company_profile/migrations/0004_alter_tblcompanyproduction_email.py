# Generated by Django 5.0.1 on 2024-02-06 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0003_appborrowmaterial_borrow_from_approval_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblcompanyproduction',
            name='email',
            field=models.EmailField(max_length=100, unique=True, verbose_name='Official email'),
        ),
    ]
