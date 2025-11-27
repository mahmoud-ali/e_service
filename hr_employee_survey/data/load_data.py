import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from hr_employee_survey.models import  Employee_Data_Emergency


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
