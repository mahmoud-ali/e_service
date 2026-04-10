from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("form15_tra", "0013_collectionform_idx_collection_receipt_number_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="collectionform",
            name="pending_payment_check_now",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Set when a user opens this collection in Pending Payment; cleared when the sync worker consumes it.",
            ),
        ),
    ]
