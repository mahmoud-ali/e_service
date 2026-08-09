from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prices', '0007_remove_banksudangoldprice_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dollarprice',
            old_name='price_in_sdg',
            new_name='buy_price_in_sdg',
        ),
        migrations.AlterField(
            model_name='dollarprice',
            name='buy_price_in_sdg',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='سعر الشراء بالجنيه'),
        ),
        migrations.AddField(
            model_name='dollarprice',
            name='sell_price_in_sdg',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='سعر البيع بالجنيه'),
        ),
    ]
