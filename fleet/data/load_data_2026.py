import csv
from datetime import datetime
from django.contrib.auth import get_user_model
from fleet.models import (
    Vehicle, VehicleAssignment, VehicleCertificate, 
    VehicleCertificateType, VehicleFuelType, VehicleMake, 
    VehicleModel, VehicleStatus
)

def get_last_year(date_obj):
    if not date_obj:
        return None
    try:
        last_year = date_obj.replace(year=date_obj.year - 1)
    except ValueError:
        last_year = date_obj.replace(month=2, day=28, year=date_obj.year - 1)
    return last_year

def parse_date(date_str):
    if not date_str or not date_str.strip():
        return None
    
    for fmt in ('%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None

def import_vehicles_2026():
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first() or User.objects.get(id=1)
    
    if not admin_user:
        print("Error: No admin user found to assign as creator.")
        return

    cert_insuranse_ejbari, _ = VehicleCertificateType.objects.get_or_create(name="تأمين اجباري")
    cert_insuranse_shamel, _ = VehicleCertificateType.objects.get_or_create(name="تأمين شامل")
    cert_license, _ = VehicleCertificateType.objects.get_or_create(name="ترخيص")

    fuel_type_binzeen, _ = VehicleFuelType.objects.get_or_create(name="بنزين")

    csv_file_path = './fleet/data/data_fleet.csv'
    
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  
        
        count = 0
        updated_count = 0
        created_count = 0
        
        for row in reader:
            if not row or len(row) < 8:
                continue
            
            try:
                maker_name = row[0].strip()
                model_name = row[1].strip()
                year_str = row[2].strip()
                license_plate = row[3].strip()
                assign_to = row[5].strip()    
                status_name = row[7].strip()   
                license_date_str = row[8].strip()
                insurance_date_str = row[9].strip()
                
                if not license_plate:
                    continue

                try:
                    year = int(year_str)
                except ValueError:
                    year = 2026 

                maker_obj, _ = VehicleMake.objects.get_or_create(name=maker_name)
                model_obj, _ = VehicleModel.objects.get_or_create(make=maker_obj, name=model_name)
                status_obj, _ = VehicleStatus.objects.get_or_create(name=status_name)

                vehicle_obj, created = Vehicle.objects.update_or_create(
                    license_plate=license_plate,
                    defaults={
                        'model': model_obj,
                        'year': year,
                        'fuel_type': fuel_type_binzeen,
                        'status': status_obj,
                        'updated_by': admin_user
                    }
                )
                
                if created:
                    vehicle_obj.created_by = admin_user
                    vehicle_obj.save()
                    created_count += 1
                else:
                    updated_count += 1

                if assign_to:
                    VehicleAssignment.objects.update_or_create(
                        vehicle=vehicle_obj,
                        defaults={
                            'assign_to': assign_to,
                            'start_date': '2026-01-01',
                            'updated_by': admin_user,
                        }
                    )
                   

                license_date = parse_date(license_date_str)
                insurance_date = parse_date(insurance_date_str)

                if insurance_date:
                    for cert_type in [cert_insuranse_ejbari, cert_insuranse_shamel]:
                        VehicleCertificate.objects.update_or_create(
                            vehicle=vehicle_obj,
                            cert_type=cert_type,
                            defaults={
                                'start_date': get_last_year(insurance_date),
                                'end_date': insurance_date,
                                'updated_by': admin_user
                            }
                        )

                if license_date:
                    VehicleCertificate.objects.update_or_create(
                        vehicle=vehicle_obj,
                        cert_type=cert_license,
                        defaults={
                            'start_date': get_last_year(license_date),
                            'end_date': license_date,
                            'updated_by': admin_user
                        }
                    )
                
                count += 1
                if count % 10 == 0:
                    print(f"Processed {count} vehicles...")
            except Exception as e:
                print(f"Error importing row {row}: {e}")

    print(f"Total Processed: {count}")
    print(f"Created: {created_count}")
    print(f"Updated: {updated_count}")

import_vehicles_2026()
