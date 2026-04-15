import csv
import django
import os
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_service.settings')
django.setup()

from traditional_app import models as tr_models
from traditional_app.models import EmployeeCategory, Employee, EmployeeJobData
from company_profile.models import LkpState
from django.contrib.auth import get_user_model
from django.db import transaction

admin_user = get_user_model().objects.get(id=1)

def clear_existing_data():
    """
    Clears existing employee data and related data.
    """
    with transaction.atomic():
        print("Clearing existing payroll details...")
        tr_models.PayrollDetail.objects.all().delete()
        print("Clearing existing job data...")
        EmployeeJobData.objects.all().delete()
        print("Clearing existing employee statuses...")
        tr_models.EmployeeStatus.objects.all().delete()
        print("Clearing existing employee bank accounts...")
        tr_models.EmployeeBankAccount.objects.all().delete()
        print("Clearing existing employee leaves...")
        tr_models.EmployeeLeave.objects.all().delete()
        print("Clearing existing employee penalties...")
        tr_models.EmployeePenalty.objects.all().delete()
        print("Clearing existing employee documents...")
        tr_models.EmployeeDocument.objects.all().delete()
        print("Clearing existing academic qualifications...")
        tr_models.AcademicQualification.objects.all().delete()
        print("Clearing existing rented vehicles (rented_for)...")
        tr_models.RentedVehicle.objects.all().delete()
        print("Clearing existing employees...")
        Employee.objects.all().delete()
        print("Cleared.")

def import_employee_data(file_name='employee_data.csv'):
    """
    Loads employee data from the specified CSV file.
    """
    association_map = {
        'الهيكل': EmployeeJobData.ASSOCIATION_STRUCTURE,
        'تعاقد': EmployeeJobData.ASSOCIATION_CONTRACT,
        'ملحق': EmployeeJobData.ASSOCIATION_SECONDMENT,
        'قوات امنية': EmployeeJobData.ASSOCIATION_SECURITY_FORCES,
        'ملحق علي الرئاسة': EmployeeJobData.ASSOCIATION_SECONDMENT_COMPANY,
    }
    with open('./traditional_app/data/'+file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            try:
                name = row['الاسم'].strip()
                category_name = row['فئة الموظف'].strip()
                association_str = row['نوع الارتباط'].strip()
                state_name = row['الولاية'].strip().replace('أ', 'ا').replace('إ', 'ا')
                job_title = row.get('المسمى الوظيفي', '').strip()

                state, _ = LkpState.objects.get_or_create(
                    name=state_name,
                    defaults={'x': 0.0, 'y': 0.0}
                )
                    
                category, _ = EmployeeCategory.objects.get_or_create(name=category_name)
                
                association_type = association_map.get(association_str, EmployeeJobData.ASSOCIATION_STRUCTURE)

                employee = Employee.objects.create(
                    name=name,
                    state=state,
                    category=category,
                    created_by=admin_user,
                    updated_by=admin_user
                )

                EmployeeJobData.objects.create(
                    employee=employee,
                    hire_date='2020-01-01',
                    association_type=association_type,
                    job_title=job_title,
                    created_by=admin_user,
                    updated_by=admin_user
                )

                yield employee
                
            except Exception as e:
                print(f"Error processing row {row}: {e}")

def run_import(file_name='employee_data.csv'):
    clear_existing_data()
    print("Starting employee data import...")
    count = 0
    for employee in import_employee_data(file_name):
        count += 1
        if count % 100 == 0:
            print(f"Imported {count} employees...")
    print(f"Finished. Total imported: {count}")

if __name__ == "__main__":
    run_import()

