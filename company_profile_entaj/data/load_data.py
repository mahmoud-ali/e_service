import csv
import datetime

from django.contrib.auth.models import Group, Permission

from django.contrib.auth import get_user_model

from company_profile_entaj.models import ForeignerPermission, ForeignerPermissionType, ForeignerRecord, TblCompanyEntaj
from workflow.data_utils import create_master_details_groups
from company_profile_entaj import admin

admin_user = get_user_model().objects.get(id=1)

def create_groups():
    create_master_details_groups('company_profile_entaj','foreignerrecord',admin.foreigner_record_main_class,admin.foreigner_record_inline_classes)

def import_foreign_data(file_name='foreign_data.csv'):
    date_format = '%d/%m/%Y'
    passport = ForeignerPermissionType.objects.filter(name='passport').first()
    if not passport:
        passport = ForeignerPermissionType.objects.create(
            name='passport',
            minimum_no_months=8,
        )
    with open('./company_profile_entaj/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                for_name = row[3]
                employment_name = row[5]
                position_name = row[6]
                department_name = row[7]
                doc_type = row[9]
                doc_id = row[10]
                doc_valid_dt = row[14]
                company_id = row[15]

                person = ForeignerRecord.objects.create(
                    company=TblCompanyEntaj.objects.get(id=company_id),
                    name=for_name,
                    position=position_name,
                    department=department_name,
                    salary=0,
                    employment_type=1 if employment_name == 'موظف دائم' else 2,
                    created_by=admin_user,
                    updated_by=admin_user,
                )

                ForeignerPermission.objects.create(
                    foreigner_record=person,
                    permission_type=passport,
                    type_id=doc_id,
                    validity_due_date=doc_valid_dt,
                    created_by=admin_user,
                    updated_by=admin_user,
                )

                # print(f"for_name: {for_name},employment_name: {employment_name},position_name: {position_name},department_name: {department_name},doc_type: {doc_type},doc_id: {doc_id},doc_valid_dt: {doc_valid_dt},company_id: {company_id}")

            except Exception as e:
                print(f"id: {id}, Exception: {e}")
