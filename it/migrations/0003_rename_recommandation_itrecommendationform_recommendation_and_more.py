# Generated by Django 5.0.2 on 2025-03-03 11:20

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it', '0002_itrecommendationform'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='itrecommendationform',
            old_name='recommandation',
            new_name='recommendation',
        ),
        migrations.AddField(
            model_name='itrecommendationform',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='itrecommendationform',
            name='priority',
            field=models.PositiveSmallIntegerField(default=1, help_text='A small integer between 1 and 10', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='developmentrequestform',
            name='state',
            field=models.IntegerField(choices=[(1, 'IT_STATE_DRAFT'), (2, 'IT_STATE_CONFIRMED'), (3, 'IT_STATE_APPROVED'), (4, 'IT_STATE_IT_MANAGER_STUDING_APPROVAL'), (5, 'IT_STATE_IT_MANAGER_STUDING_REJECTION'), (6, 'IT_STATE_IT_MANAGER_RECOMMENDATION'), (7, 'IT_STATE_PQI_MANAGER_CHANGE_REQUEST'), (8, 'IT_STATE_PQI_MANAGER_APPROVAL')], default=1, verbose_name='record_state'),
        ),
        migrations.CreateModel(
            name='ItRejectionForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('reason', models.TextField()),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('form', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='it_rejection_form', to='it.developmentrequestform', verbose_name='DevelopmentRequestForm')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
