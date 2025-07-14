import csv
from datetime import datetime

from django.contrib.auth import get_user_model

from fleet.models import Vehicle, VehicleAssignment, VehicleCertificate, VehicleCertificateType, VehicleMake, VehicleModel, VehicleStatus

admin_user = get_user_model().objects.get(id=1)

def get_last_year(date_str):
    date = datetime.fromisoformat(date_str).date()

    try:
        # Try to replace the year directly
        last_year = date.replace(year=date.year - 1)
    except ValueError:
        # Handles Feb 29 case by moving to Feb 28
        last_year = date.replace(month=2, day=28, year=date.year - 1)

    return last_year

def import_vehicles():
    cert_insuranse_ejbari = VehicleCertificateType.objects.create(name="تأمين اجباري")
    cert_insuranse_shamel = VehicleCertificateType.objects.create(name="تأمين شامل")
    cert_license = VehicleCertificateType.objects.create(name="ترخيص")
    with open('./fleet/data/vehicle.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            # print(', '.join(row[:10]))
            maker = row[0].strip()
            model = row[1].strip()
            year = int(row[2].strip())
            license_plate = row[3].strip()
            assign_to = row[4].strip()
            geo = row[5]
            status = row[6]
            license_date = row[7].strip()
            insuranse_date = row[8].strip()
            is_jiha = row[9].strip()
            # print(maker,model,year,license_plate,assign_to,geo,status,license_date,insuranse_date,is_jiha)

            maker_obj, created = VehicleMake.objects.get_or_create(name=maker)
            model_obj, created = VehicleModel.objects.get_or_create(make=maker_obj,name=model)
            status_obj, created = VehicleStatus.objects.get_or_create(name=status)

            vehicle_obj = Vehicle.objects.create(
                model=model_obj,
                year=year,
                license_plate=license_plate,
                status=status_obj,
                created_by=admin_user,
                updated_by=admin_user
            )

            VehicleAssignment.objects.create(
                vehicle=vehicle_obj,
                assign_to=assign_to,
                start_date='2025-01-01',
                created_by=admin_user,
                updated_by=admin_user
            )

            VehicleCertificate.objects.get_or_create(
                vehicle=vehicle_obj,
                cert_type=cert_insuranse_ejbari,
                start_date=get_last_year(insuranse_date),
                end_date=insuranse_date,
                created_by=admin_user,
                updated_by=admin_user
            )
            VehicleCertificate.objects.get_or_create(
                vehicle=vehicle_obj,
                cert_type=cert_insuranse_shamel,
                start_date=get_last_year(insuranse_date),
                end_date=insuranse_date,
                created_by=admin_user,
                updated_by=admin_user
            )
            VehicleCertificate.objects.get_or_create(
                vehicle=vehicle_obj,
                cert_type=cert_license,
                start_date=get_last_year(license_date),
                end_date=license_date,
                created_by=admin_user,
                updated_by=admin_user
            )
