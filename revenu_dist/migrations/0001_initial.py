# Generated by Django 5.0.2 on 2024-09-02 09:21

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LkpPartner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Partner',
                'verbose_name_plural': 'Partners',
            },
        ),
        migrations.CreateModel(
            name='LkpRevenuType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Revenu type',
                'verbose_name_plural': 'Revenu types',
            },
        ),
        migrations.CreateModel(
            name='LkpRevenuTypeDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent', models.IntegerField(validators=[django.core.validators.MinValueValidator(limit_value=0), django.core.validators.MaxValueValidator(limit_value=100)], verbose_name='percent')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='revenu_dist.lkprevenutype')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='revenu_dist.lkppartner')),
            ],
            options={
                'verbose_name': 'Revenu type detail',
                'verbose_name_plural': 'Revenu type details',
            },
        ),
        migrations.CreateModel(
            name='TblRevenu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('date', models.DateField(verbose_name='date')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('amount', models.FloatField(verbose_name='amount')),
                ('currency', models.IntegerField(choices=[(1, 'sdg'), (2, 'euro'), (3, 'dollar')], default=1, verbose_name='currency')),
                ('source', models.CharField(max_length=100, verbose_name='source')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('revenu_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='revenu_dist.lkprevenutype')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
            ],
            options={
                'verbose_name': 'Revenu detail',
                'verbose_name_plural': 'Revenu details',
            },
        ),
        migrations.CreateModel(
            name='TblRevenuDist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='amount')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='revenu_dist.tblrevenu')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='revenu_dist.lkppartner')),
            ],
            options={
                'verbose_name': 'Revenu distribution',
                'verbose_name_plural': 'Revenu distribution',
            },
        ),
    ]
