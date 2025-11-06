from django.db import migrations

def populate_suggested_items(apps, schema_editor):
    SuggestedItem = apps.get_model('needs_request', 'SuggestedItem')
    items = [
        'Laptop',
        'Mouse',
        'Keyboard',
        'Monitor',
        'Chair',
        'Desk',
        'Printer',
        'Scanner',
    ]
    for item_name in items:
        SuggestedItem.objects.create(name=item_name)

class Migration(migrations.Migration):

    dependencies = [
        ('needs_request', '0004_suggesteditem'),
    ]

    operations = [
        migrations.RunPython(populate_suggested_items),
    ]
