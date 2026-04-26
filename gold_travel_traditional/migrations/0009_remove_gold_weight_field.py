from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel_traditional', '0008_remove_old_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appmovegoldtraditional',
            name='gold_weight_in_gram',
        ),
    ]
