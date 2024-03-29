# Generated by Django 5.0.1 on 2024-02-06 22:18

import company_profile.models
import django.db.models.deletion
import django_fsm
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile', '0015_apptakhali'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AppTamdeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('state', django_fsm.FSMField(choices=[('submitted', 'Submitted state'), ('accepted', 'Accepted state'), ('approved', 'Approved state'), ('rejected', 'Rejected state')], default='submitted', max_length=50, verbose_name='application_state')),
                ('notify', models.BooleanField(default=False, editable=False, verbose_name='notify_user')),
                ('tamdeed_from', models.DateField(verbose_name='tamdeed_from')),
                ('tamdeed_to', models.DateField(verbose_name='tamdeed_to')),
                ('cause_for_tamdeed', models.TextField(max_length=1000, verbose_name='cause_for_tamdeed')),
                ('approved_work_plan_file', models.FileField(upload_to=company_profile.models.company_applications_path, verbose_name='approved_work_plan_file')),
                ('tnazol_file', models.FileField(upload_to=company_profile.models.company_applications_path, verbose_name='tnazol_file')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='company_profile.tblcompanyproduction', verbose_name='company')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
            ],
            options={
                'verbose_name': 'Application: Tamdeed',
                'verbose_name_plural': 'Application: Tamdeed',
                'ordering': ['-id'],
            },
        ),
    ]
