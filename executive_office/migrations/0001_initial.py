# Generated by Django 5.0.2 on 2024-12-30 09:36

import django.db.models.deletion
import executive_office.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcedureType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'verbose_name': 'procedure_type',
                'verbose_name_plural': 'procedure_types',
            },
        ),
        migrations.CreateModel(
            name='SenderEntity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='executive_user', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
            },
        ),
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('start_date', models.DateTimeField(verbose_name='start_date')),
                ('expected_due_date', models.DateTimeField(verbose_name='expected_due_date')),
                ('finish_date', models.DateTimeField(null=True, verbose_name='finish_date')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created_by')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated_by')),
                ('procedure_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='executive_office.proceduretype', verbose_name='procedure_type')),
                ('sender_entity', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='executive_office.senderentity', verbose_name='sender_entity')),
            ],
            options={
                'verbose_name': 'inbox',
                'verbose_name_plural': 'inbox',
            },
        ),
        migrations.CreateModel(
            name='InboxAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_file', models.FileField(upload_to=executive_office.models.inbox_path, verbose_name='attachment_file')),
                ('inbox', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='executive_office.inbox', verbose_name='inbox')),
            ],
            options={
                'verbose_name': 'inbox attachment',
                'verbose_name_plural': 'inbox attachments',
            },
        ),
        migrations.CreateModel(
            name='InboxTasks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('order', models.IntegerField(choices=[(1, 'order_procedure'), (2, 'order_followup')], verbose_name='order')),
                ('assign_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='executive_office.contact', verbose_name='assign_to')),
                ('inbox', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='executive_office.inbox', verbose_name='inbox')),
            ],
            options={
                'verbose_name': 'inbox task',
                'verbose_name_plural': 'inbox tasks',
            },
        ),
        migrations.CreateModel(
            name='ProcedureTypeTasksTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('order', models.IntegerField(choices=[(1, 'order_procedure'), (2, 'order_followup')], verbose_name='order')),
                ('assign_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='executive_office.contact', verbose_name='assign_to')),
                ('procedure_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='executive_office.proceduretype', verbose_name='procedure_type')),
            ],
            options={
                'verbose_name': 'procedure type task template',
                'verbose_name_plural': 'procedure type task templates',
            },
        ),
    ]
