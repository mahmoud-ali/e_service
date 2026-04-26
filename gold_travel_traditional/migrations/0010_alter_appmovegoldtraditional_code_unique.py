from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel_traditional', '0009_remove_gold_weight_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appmovegoldtraditional',
            name='code',
            field=models.CharField(max_length=20, unique=True, verbose_name='code'),
        ),
    ]
