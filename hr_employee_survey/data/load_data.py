import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from hr_employee_survey.models import  Employee_Data_Emergency
from hr.models import  EmployeeBasic


admin_user = get_user_model().objects.get(id=1)

def show_data():
    with open('./hr_employee_survey/data/employee_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            print(', '.join(row[1:3]))
def empty_database():
    Employee_Data_Emergency.objects.all().delete()
 

def import_employees():

    with open('./hr_employee_survey/data/employee_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            name = row[0].strip()
            job_title = row[1].strip()
            email = row[2].strip()
            direct_manager_email = row[3].strip()
  
            try:
                Employee_Data_Emergency.objects.create(
                   name=name,job_title=job_title,email=email,direct_manager_email=direct_manager_email
                )
            except Exception as e:
                print(f'name: {name}, Exception: {e}')


def update_email(filename='email.csv'):    
    with open('./hr_employee_survey/data/mubasher.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                id = row[0].strip()
                email = row[2].strip()

                obj = Employee_Data_Emergency.objects.get(id=id)
                obj.email = email

                obj.save()

                #print(id)
            except:
                print("error",row)



def import_from_employee_basic():

    with open('./hr_employee_survey/data/employee_basic.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            id = row[0].strip()

            try:
                emp = EmployeeBasic.objects.get(code=id)
                Employee_Data_Emergency.objects.create(
                   name=emp.name,job_title='-',email=emp.email
                )
            except Exception as e:
                print(f'name: {row}, Exception: {e}')


def import_employees2():

    with open('./hr_employee_survey/data/employee_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            name = row[0].strip()
            job_title = row[1].strip()
            email = row[2].strip()
            direct_manager_email = row[3].strip()
            edara_3ama = row[5].strip()

            try:
                emp = EmployeeBasic.objects.get(email=email)
                name = emp.name
    
                try:
                    x = Employee_Data_Emergency.objects.get(email=email)
                    x.name = name
                    x.direct_manager_email = direct_manager_email
                    x.edara_3ama = edara_3ama
                    x.save()

                except Employee_Data_Emergency.DoesNotExist as e:
                    Employee_Data_Emergency.objects.create(
                        name=name,job_title=job_title,email=email,direct_manager_email=direct_manager_email,edara_3ama=edara_3ama
                    )

                    print(f'name: {name}, email: {email}, Exception: {e}')

            except Exception as e:
                print(f'emp: {emp}, Exception: {e}')
