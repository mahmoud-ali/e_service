import csv

from django.contrib.auth import get_user_model

from hr.models import EmployeeBasic
from it.models import AccessPoint, Computer, Conversation, EmployeeComputer, Peripheral

def clone_computer(employee:EmployeeBasic,src:Computer):
    obj = Computer.objects.create(
        code=f"{src.type}/{employee.code}",
        type=src.type,
        template=src.template,
    )

    EmployeeComputer.objects.create(
        employee=employee,
        computer=obj,
    )

    for peripheral_obj in Peripheral.objects.filter(computer=src):
        Peripheral.objects.create(
            computer=obj,
            type=peripheral_obj.type,
            name=peripheral_obj.name,
            connectivity_type=peripheral_obj.connectivity_type,
            specifications=peripheral_obj.specifications,
        )

    for access_point_obj in AccessPoint.objects.filter(computer=src):
        AccessPoint.objects.create(
            computer=obj,
            name=access_point_obj.name,
            model=access_point_obj.model,
        )

    return obj

def import_employees_computer(filename='emp_mobasher.csv'):    
    laptop_obj = Computer.objects.get(id=2)
    desktop_obj = Computer.objects.get(id=3)
    with open(f'./it/data/'+filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                code = int(row[0])
                emp = EmployeeBasic.objects.get(code=code)
                laptop = row[2]
                desktop = row[3]
                access_points_str = str(row[4])

                obj = None

                if laptop:
                    obj = clone_computer(emp,laptop_obj)
                if desktop:
                    obj = clone_computer(emp,desktop_obj)

                if obj:
                    for access_point_name in access_points_str.split(","):
                        AccessPoint.objects.create(
                            computer=obj,
                            name=access_point_name,
                        )
            except Exception as e:
                print('not imported',e)

def delete_employees_computer():
    AccessPoint.objects.all().delete()
    Peripheral.objects.all().delete()
    Conversation.objects.all().delete()
    EmployeeComputer.objects.all().delete()
    Computer.objects.all().delete()
    