from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("form15_tra", "0014_collectionform_pending_payment_check_now"),
    ]

    operations = [
        migrations.AddField(
            model_name="collectionform",
            name="invoice_generated_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]

