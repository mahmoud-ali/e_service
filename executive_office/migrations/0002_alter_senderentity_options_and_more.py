# Generated by Django 5.0.2 on 2024-12-30 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('executive_office', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='senderentity',
            options={'verbose_name': 'sender_entity', 'verbose_name_plural': 'sender_entities'},
        ),
        migrations.AlterField(
            model_name='inbox',
            name='expected_due_date',
            field=models.DateField(verbose_name='expected_due_date'),
        ),
        migrations.AlterField(
            model_name='inbox',
            name='finish_date',
            field=models.DateField(null=True, verbose_name='finish_date'),
        ),
        migrations.AlterField(
            model_name='inbox',
            name='start_date',
            field=models.DateField(verbose_name='start_date'),
        ),
    ]
