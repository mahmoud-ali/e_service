# Generated by Django 5.1.7 on 2025-03-23 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_profile_exploration', '0005_alter_appworkplan_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appworkplan',
            name='state',
            field=models.IntegerField(choices=[(1, 'draft'), (4, 'توجيه م.ا.ع'), (5, 'دراسة اولية'), (6, 'دراسة فنية'), (7, 'مراجعة الطلب بواسطة الشركة'), (8, 'تحرير شهادة القبول/الرفض')], default=1, verbose_name='record_state'),
        ),
    ]
