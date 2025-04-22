import csv

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from company_profile.models import TblCompany

from django.conf import settings

from production_control.models import GoldProductionForm, GoldShippingForm, LkpMoragib
from django.contrib.auth import get_user_model

admin_user = get_user_model().objects.get(id=1)

def import_moragbin(company_type=None,file_name='mokhlafat.csv'):
    if not company_type or company_type not in(TblCompany.COMPANY_TYPE_ENTAJ,TblCompany.COMPANY_TYPE_EMTIAZ,TblCompany.COMPANY_TYPE_MOKHALFAT,TblCompany.COMPANY_TYPE_SAGEER):
        print('Please pass correct company type!')
        return

    with open('./production_control/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers

        User = get_user_model()
        moragib_group = Group.objects.get(name='production_control_auditor')

        for row in reader:
            try:
                code = row[0].strip()
                name = row[1].strip()
                email = row[2].strip()

                try:
                    user = User.objects.get(email=email)
                except:
                    user = User.objects.create_user(email, email, settings.ACCOUNT_DEFAULT_PASSWORD)

                user.is_staff = True
                user.save()

                moragib_group.user_set.add(user)
                
                moragib,created = LkpMoragib.objects.get_or_create(
                    user=user,
                    name=name,
                    emp_code=code,
                    company_type=company_type,
                )

                print(f"Created successfully, user: {user}, moragib: {moragib}, created: {created}")

            except Exception as e:
                print(f"id: {code}, Exception: {e}")

from workflow.data_utils import create_master_details_groups
from production_control import admin

def create_groups():
    create_master_details_groups('production_control','goldproductionform',admin.production_main_class,admin.production_inline_classes)
    create_master_details_groups('production_control','goldshippingform',admin.move_main_class,admin.move_inline_classes)

def update_one_license_company():
    qs = GoldProductionForm.objects.exclude(license__isnull=False)
    for obj in qs:
        license = obj.company.tblcompanyproductionlicense_set.first()
        if license:
            print("*",obj.company.tblcompanyproductionlicense_set.first())
            obj.license = obj.company.tblcompanyproductionlicense_set.first()
            obj.save()

    qs = GoldShippingForm.objects.exclude(license__isnull=False)
    for obj in qs:
        license = obj.company.tblcompanyproductionlicense_set.first()
        if license:
            print("*",obj.company.tblcompanyproductionlicense_set.first())
            obj.license = obj.company.tblcompanyproductionlicense_set.first()
            obj.save()

    # qs = GoldShippingForm.objects.all()
    # for obj in qs:
    #     company = obj.license.company
    #     if company and obj.company != company:
    #         print("*",company)
    #         obj.company = company
    #         obj.save()

if __name__ == '__main__':
    create_groups()