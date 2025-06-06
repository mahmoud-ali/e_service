# Generated by Django 5.1.7 on 2025-05-04 08:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hse_companies', '0019_alter_incidentinjured_injured_surname'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentInjuredDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nature_of_injury', models.TextField(blank=True, null=True, verbose_name='طبيعة الاصابة او المرض ( مثلا تمزق ، كسر، جرح) Nature of Injury or Illness (e.g. fracture, strain/sprain, bruising)')),
                ('bodily_location', models.CharField(blank=True, max_length=100, null=True, verbose_name='مكان الاصابة بالجسم او المرض(مثلا اليد اليمنى، اسفل الظهر، الرئتين) Bodily Location of Injury or Illness (e.g. right leg, lower back)')),
                ('first_aid_details', models.TextField(blank=True, null=True, verbose_name='تفاصيل الاسعافات الاولية المقدمة للمصاب Details of Any First Aid Treatment Provided')),
                ('first_aider_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='اسم المسعف Name of First Aider')),
                ('hospital_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='في حالة تم نقله للمستشفى، اسم المستشفى If admitted to Hospital,hospital name')),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_injured_details', to='hse_companies.incidentinfo')),
            ],
            options={
                'verbose_name': 'تفاصيل الاصابة/المرض المهني  Details of Injury/illness',
                'verbose_name_plural': 'تفاصيل الاصابة/المرض المهني  Details of Injury/illness',
            },
        ),
        migrations.CreateModel(
            name='IncidentInjuredPerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('injured_surname', models.CharField(max_length=100, verbose_name='إسم المصاب Injured Surname')),
                ('injured_position', models.CharField(blank=True, max_length=100, null=True, verbose_name='الوظيفة Position')),
                ('injured_experience_years', models.PositiveIntegerField(blank=True, null=True, verbose_name=' الخبرة بالأعوام Experience in Years')),
                ('injured_date_of_birth', models.DateField(blank=True, null=True, verbose_name='تاريخ الميلاد Date of Birth')),
                ('injured_employment_basis', models.SmallIntegerField(blank=True, choices=[(1, 'دوام كامل Full Time'), (2, 'دوام جزئي Part Time'), (3, 'يومية Casual'), (4, 'متعاقد Contractor')], null=True, verbose_name='نوع التوظيف Basis of Employment')),
                ('lost_time_injury', models.BooleanField(default=False, verbose_name='هل تسببت الإصابة في التغيب عن العمل؟ Did this incident cause of Lost Time of working days?')),
                ('lost_days', models.PositiveIntegerField(blank=True, null=True, verbose_name='في حال كانت الإجابة نعم حدد عدد الأيام حتى تاريخ هذا التقرير If yes, specify Number of lost days up to this report')),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_injured_person', to='hse_companies.incidentinfo')),
            ],
            options={
                'verbose_name': 'تفاصيل الشخص المصاب Details of Injured Person',
                'verbose_name_plural': 'تفاصيل الشخص المصاب Details of Injured Person',
            },
        ),
        migrations.CreateModel(
            name='IncidentInjuredPPE',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ppe_gloves', models.BooleanField(default=False, verbose_name='قفازات Gloves')),
                ('ppe_helmet', models.BooleanField(default=False, verbose_name='خوذة Helmet')),
                ('ppe_safety_cloth', models.BooleanField(default=False, verbose_name='لبس السلامة Safety cloth')),
                ('ppe_safety_shoes', models.BooleanField(default=False, verbose_name='حذاء السلامة Safety Shoes')),
                ('ppe_face_protection', models.BooleanField(default=False, verbose_name='نظارة/واقي وجهGlass/face Protection')),
                ('ppe_ear_protection', models.BooleanField(default=False, verbose_name=' واقي الاذن Ear Protection')),
                ('ppe_mask', models.BooleanField(default=False, verbose_name='كمامة Mask')),
                ('ppe_other', models.CharField(blank=True, max_length=100, null=True, verbose_name='اخرى Other')),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_injured_ppe', to='hse_companies.incidentinfo')),
            ],
            options={
                'verbose_name': 'معدات الحماية الشخصية المستخدمة اثناء الحادث protective equipment’s used during the Incident',
                'verbose_name_plural': 'معدات الحماية الشخصية المستخدمة اثناء الحادث protective equipment’s used during the Incident',
            },
        ),
        migrations.DeleteModel(
            name='IncidentInjured',
        ),
    ]
