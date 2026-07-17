# Generated migration - MeltBatchDetail model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel_traditional', '0049_appmovegoldtraditional_arrival_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeltBatchDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alloy_weight_gram', models.FloatField(verbose_name='وزن السبيكة بالجرام')),
                ('alloy_shape', models.IntegerField(choices=[(1, 'دائري'), (2, 'مستطيل'), (3, 'أخرى')], verbose_name='شكل السبيكة')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='gold_travel_traditional.meltbatch', verbose_name='master')),
            ],
            options={
                'verbose_name': 'تفاصيل السبيكة الناتجة',
                'verbose_name_plural': 'تفاصيل السبائك الناتجة',
            },
        ),
    ]
