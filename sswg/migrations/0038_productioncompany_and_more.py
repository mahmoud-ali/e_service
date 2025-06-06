# Generated by Django 5.2.1 on 2025-06-01 15:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0129_alter_tblcompanyproductionlicense_geom'),
        ('sswg', '0037_alter_basicformexport_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionCompany',
            fields=[
            ],
            options={
                'verbose_name': 'شركة امتياز منتجة',
                'verbose_name_plural': 'شركات الامتياز المنتجة',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('company_profile.tblcompanyproduction',),
        ),
        migrations.RemoveField(
            model_name='companydetails',
            name='basic_form_export_emtiaz',
        ),
        migrations.RemoveField(
            model_name='transferrelocationformdata',
            name='basic_form_export_emtiaz',
        ),
        migrations.CreateModel(
            name='CompanyDetailsEmtiaz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('surrogate_name', models.CharField(max_length=255, verbose_name='Surrogate Name')),
                ('surrogate_id_type', models.IntegerField(choices=[(1, 'identity_passport'), (2, 'identity_personal'), (3, 'identity_national_id'), (4, 'identity_driving_license')], verbose_name='ID Type')),
                ('surrogate_id_val', models.CharField(max_length=50, verbose_name='ID Value')),
                ('surrogate_id_phone', models.CharField(max_length=50, verbose_name='Contact Phone')),
                ('total_weight', models.FloatField(default=0, verbose_name='الوزن الكلي')),
                ('total_count', models.IntegerField(default=0, verbose_name='عدد السبائك')),
                ('basic_form_export_emtiaz', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='company_details_export_emtiaz', to='sswg.basicformexportcompany', verbose_name='SSWG Basic Form')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sswg.productioncompany', verbose_name='Company Name')),
            ],
            options={
                'verbose_name': 'SSWG CompanyDetails',
                'verbose_name_plural': 'SSWG CompanyDetails',
            },
        ),
    ]
