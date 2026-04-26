from django.db import migrations

def remove_old_data(apps, schema_editor):
    AppMoveGoldTraditional = apps.get_model('gold_travel_traditional', 'AppMoveGoldTraditional')
    # Assuming 'old' data means all existing records before this cleanup, 
    # or you might want to specify a criteria like created_at or id range.
    # If the goal is to just clear the table:
    AppMoveGoldTraditional.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('gold_travel_traditional', '0007_alter_appmovegoldtraditional_attachement_file_and_more'),
    ]

    operations = [
        migrations.RunPython(remove_old_data),
    ]
