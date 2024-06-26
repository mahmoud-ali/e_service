# Generated by Django 5.0.2 on 2024-05-01 11:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0063_tblcompanyproductionlicense_mineral'),
        ('pa', '0011_tblcompanypaymentdetail_attachement_file_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblcompanycommitmentmaster',
            name='currency',
            field=models.CharField(choices=[('sdg', 'sdg'), ('euro', 'euro'), ('dollar', 'dollar')], default='euro', max_length=10, verbose_name='currency'),
        ),
        migrations.AlterField(
            model_name='tblcompanypaymentmaster',
            name='currency',
            field=models.CharField(choices=[('sdg', 'sdg'), ('euro', 'euro'), ('dollar', 'dollar')], default='euro', max_length=10, verbose_name='currency'),
        ),
        migrations.AlterField(
            model_name='tblcompanyrequestmaster',
            name='currency',
            field=models.CharField(choices=[('sdg', 'sdg'), ('euro', 'euro'), ('dollar', 'dollar')], default='euro', max_length=10, verbose_name='currency'),
        ),
        migrations.CreateModel(
            name='TblCompanyOpenningBalanceMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('currency', models.CharField(choices=[('sdg', 'sdg'), ('euro', 'euro'), ('dollar', 'dollar')], default='euro', max_length=10, verbose_name='currency')),
                ('state', models.CharField(choices=[('draft', 'draft'), ('confirm', 'confirm')], default='draft', max_length=10, verbose_name='record_state')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='company_profile.tblcompanyproduction', verbose_name='company')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
            ],
            options={
                'verbose_name': 'Openning balance',
                'verbose_name_plural': 'Openning balances',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TblCompanyOpenningBalanceDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_factor', models.FloatField(verbose_name='amount_factor')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pa.lkpitem', verbose_name='financial item')),
                ('commitment_master', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pa.tblcompanyopenningbalancemaster')),
            ],
            options={
                'verbose_name': 'Openning balance detail',
                'verbose_name_plural': 'Openning balance details',
                'ordering': ['id'],
            },
        ),
        migrations.AddIndex(
            model_name='tblcompanyopenningbalancemaster',
            index=models.Index(fields=['company'], name='pa_tblcompa_company_1d5190_idx'),
        ),
    ]
