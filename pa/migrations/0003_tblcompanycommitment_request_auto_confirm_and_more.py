# Generated by Django 5.0.2 on 2024-03-30 17:08

import django.db.models.deletion
import pa.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pa', '0002_tblcompanycommitment_state_tblcompanypayment_state_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tblcompanycommitment',
            name='request_auto_confirm',
            field=models.BooleanField(default=False, verbose_name='request_auto_confirm'),
        ),
        migrations.AddField(
            model_name='tblcompanycommitment',
            name='request_interval',
            field=models.CharField(choices=[('manual', 'manual'), ('year', 'yearly')], default='manual', max_length=10, verbose_name='interval'),
        ),
        migrations.AddField(
            model_name='tblcompanycommitment',
            name='request_next_interval_dt',
            field=models.DateField(null=True, verbose_name='next_interval_dt'),
        ),
        migrations.AlterField(
            model_name='tblcompanycommitment',
            name='state',
            field=models.CharField(choices=[('draft', 'draft'), ('confirm', 'confirm')], default='draft', max_length=10, verbose_name='record_state'),
        ),
        migrations.AlterField(
            model_name='tblcompanypayment',
            name='amount',
            field=models.FloatField(validators=[pa.models.validate_positive], verbose_name='amount'),
        ),
        migrations.AlterField(
            model_name='tblcompanypayment',
            name='excange_rate',
            field=models.FloatField(default=1, validators=[pa.models.validate_positive], verbose_name='excange_rate'),
        ),
        migrations.AlterField(
            model_name='tblcompanypayment',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pa.tblcompanyrequest', verbose_name='request'),
        ),
        migrations.AlterField(
            model_name='tblcompanypayment',
            name='state',
            field=models.CharField(choices=[('draft', 'draft'), ('confirm', 'confirm')], default='draft', max_length=10, verbose_name='record_state'),
        ),
        migrations.AlterField(
            model_name='tblcompanyrequest',
            name='amount',
            field=models.FloatField(validators=[pa.models.validate_positive], verbose_name='amount'),
        ),
        migrations.AlterField(
            model_name='tblcompanyrequest',
            name='state',
            field=models.CharField(choices=[('draft', 'draft'), ('confirm', 'confirm')], default='draft', max_length=10, verbose_name='record_state'),
        ),
    ]