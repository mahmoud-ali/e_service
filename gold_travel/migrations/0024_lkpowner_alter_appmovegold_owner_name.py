# Generated by Django 5.1 on 2024-11-17 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel', '0023_alter_appmovegold_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='LkpOwner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'verbose_name': 'owner_name',
                'verbose_name_plural': 'owner_name',
            },
        ),
        migrations.AlterField(
            model_name='appmovegold',
            name='owner_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='owner_name'),
        ),
    ]