from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel_traditional', '0048_appmovegoldtraditional_arrival_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='appmovegoldtraditional',
            name='arrival_time',
            field=models.DateTimeField(blank=True, editable=False, null=True, verbose_name='وقت الوصول'),
        ),
    ]
