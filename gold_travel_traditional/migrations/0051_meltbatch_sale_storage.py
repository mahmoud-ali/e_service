# Generated migration - add sale and storage FK to MeltBatch

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel_traditional', '0050_meltbatchdetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='meltbatch',
            name='sale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='melt_batches', to='gold_travel_traditional.sale', verbose_name='فاتورة البيع'),
        ),
        migrations.AddField(
            model_name='meltbatch',
            name='storage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='melt_batches', to='gold_travel_traditional.storage', verbose_name='شهادة تخزين'),
        ),
    ]
