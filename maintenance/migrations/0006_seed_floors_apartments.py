from django.db import migrations

def create_initial_floors_and_apartments(apps, schema_editor):
    Floor = apps.get_model('maintenance', 'Floor')
    Apartment = apps.get_model('maintenance', 'Apartment')
    
    floors_data = [
        ('الطابق الأرضي', 0, ['شقة 001', 'شقة 002', 'شقة 003', 'مكتب الاستقبال', 'القاعة الرئيسية']),
        ('الطابق الأول', 1, ['شقة 101', 'شقة 102', 'شقة 103', 'شقة 104', 'شقة 105']),
        ('الطابق الثاني', 2, ['شقة 201', 'شقة 202', 'شقة 203', 'شقة 204', 'شقة 205']),
        ('الطابق الثالث', 3, ['شقة 301', 'شقة 302', 'شقة 303', 'شقة 304', 'شقة 305']),
        ('الطابق الرابع', 4, ['شقة 401', 'شقة 402', 'شقة 403', 'شقة 404', 'شقة 405']),
        ('الطابق الخامس', 5, ['شقة 501', 'شقة 502', 'شقة 503', 'شقة 504', 'شقة 505']),
    ]
    
    for floor_name, order, apt_names in floors_data:
        floor_obj, _ = Floor.objects.get_or_create(
            name=floor_name,
            defaults={'order': order}
        )
        for apt_name in apt_names:
            Apartment.objects.get_or_create(
                floor=floor_obj,
                name=apt_name
            )

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0005_apartment_floor_technicaltechnician_and_more'),
    ]

    operations = [
        migrations.RunPython(create_initial_floors_and_apartments, reverse_code=reverse_func),
    ]
