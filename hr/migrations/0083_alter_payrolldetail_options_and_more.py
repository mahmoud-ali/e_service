# Generated by Django 5.0.2 on 2024-10-23 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0082_alter_payrolldetail_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payrolldetail',
            options={'ordering': ['employee__code'], 'verbose_name': 'Payroll detail', 'verbose_name_plural': 'Payroll details'},
        ),
        migrations.AlterModelOptions(
            name='payrolldetailwi7datmosa3ida',
            options={},
        ),
        migrations.RemoveConstraint(
            model_name='payrolldetailwi7datmosa3ida',
            name='unique_employee_payroll',
        ),
        migrations.AddConstraint(
            model_name='payrolldetail',
            constraint=models.UniqueConstraint(fields=('payroll_master', 'employee'), name='unique_employee_payroll'),
        ),
    ]