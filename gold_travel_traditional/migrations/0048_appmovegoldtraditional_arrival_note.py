from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel_traditional', '0047_sale_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='appmovegoldtraditional',
            name='arrival_note',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='ملاحظة التوصيل'),
        ),
    ]
