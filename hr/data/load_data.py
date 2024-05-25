import csv

from django.contrib.auth import get_user_model

from ..models import MosamaWazifi,Edara3ama,Edarafar3ia,EmployeeBasic,Settings

def show_data():
    with open('./hr/data/employee.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            print(', '.join(row[1:8]))

def import_employees():
    admin_user = get_user_model().objects.get(id=1)

    # EmployeeBasic.objects.delete()

    with open('./hr/data/employee.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            id = row[0].strip()
            name = row[1].strip()
            mosama_wazifi = row[2].strip()
            edara_3ama = row[3].strip()
            edara_far3ia = row[4].strip()
            draja_wazifia = int(row[5])
            alawa_sanawia = int(row[6])
            tarikh_ta3in = row[7].strip()

            mosama_wazifi_obj, created = MosamaWazifi.objects.get_or_create(name=mosama_wazifi)
            edara_3ama_obj, created = Edara3ama.objects.get_or_create(name=edara_3ama)
            edara_far3ia_obj, created = Edarafar3ia.objects.get_or_create(name=edara_far3ia,edara_3ama=edara_3ama_obj)

            try:
                EmployeeBasic.objects.create(
                    name=name,mosama_wazifi=mosama_wazifi_obj,edara_3ama=edara_3ama_obj,edara_far3ia=edara_far3ia_obj,\
                    draja_wazifia=draja_wazifia,alawa_sanawia=alawa_sanawia,tarikh_ta3in=tarikh_ta3in,\
                    created_by=admin_user,updated_by=admin_user
                )
            except Exception as e:
                print(f'Id: {id}, Exception: {e}')
