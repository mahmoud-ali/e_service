# Generated by Django 5.0.2 on 2024-08-15 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0067_employeesalafiat_no3_2lsalafia'),
    ]

    operations = [
        migrations.AddField(
            model_name='payrolldetail',
            name='salafiat_sandog',
            field=models.FloatField(default=0, verbose_name='salafiat_sandog'),
        ),
        migrations.AlterField(
            model_name='employeebasic',
            name='status',
            field=models.IntegerField(choices=[(1, 'STATUS_ACTIVE'), (2, 'STATUS_MA3ASH'), (3, 'STATUS_TAGA3D_EKHTIARI'), (4, 'STATUS_ESTIKALA'), (5, 'STATUS_3DAM_ELIAGA_ELTIBIA'), (6, 'STATUS_ELFASL'), (7, 'STATUS_ENTIHA2_2L3AGD'), (8, 'STATUS_SHAGL_MANSAB_DASTORY'), (9, 'STATUS_ELWAFAH'), (10, 'STATUS_FOGDAN_ELJENSIA_ELSODANIA'), (11, 'STATUS_ENHA2_ENTIDAB'), (12, 'STATUS_NAGL'), (13, 'STATUS_2L7AG'), (14, 'STATUS_EJAZA_MIN_GAIR_MORATAB')], default=1, verbose_name='status'),
        ),
    ]