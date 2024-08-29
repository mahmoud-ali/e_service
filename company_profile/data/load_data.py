import csv

from django.contrib.auth import get_user_model

from ..models import LkpCompanyProductionStatus, LkpNationality, TblCompany, TblCompanyProduction

admin_user = get_user_model().objects.get(id=1)

def import_companies(company_type=None,file_name='companies.csv'):
    if not company_type or company_type not in(TblCompany.COMPANY_TYPE_ENTAJ,TblCompany.COMPANY_TYPE_EMTIAZ,TblCompany.COMPANY_TYPE_MOKHALFAT,TblCompany.COMPANY_TYPE_SAGEER):
        print('Please pass correct company type!')
        return
    
    with open('./company_profile/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            name_ar = row[0].strip()
            name_en = row[1].strip()
            nationality_str = row[2].strip()
            address = row[3].strip()
            website = row[4].strip()
            manager_name = row[5]
            manager_phone = row[6]
            rep_name = row[7].strip()
            rep_phone = row[8]
            email = row[9]
            status_str = row[10]

            nationality, created = LkpNationality.objects.get_or_create(name=nationality_str)
            status, created = LkpCompanyProductionStatus.objects.get_or_create(name=status_str)

            try:
                company = TblCompanyProduction.objects.create(
                    company_type=company_type,
                    name_ar=name_ar,
                    name_en=name_en,
                    address=address,
                    website=website,
                    manager_name=manager_name,
                    manager_phone=manager_phone,
                    rep_name=rep_name,
                    rep_phone=rep_phone,
                    email=email,
                    status=status,  
                    created_by=admin_user,
                    updated_by=admin_user
                )
                company.nationality.set([nationality])
            except Exception as e:
                print(f'name_ar: {name_ar}, name_en: {name_en}, Exception: {e}')

def import_licenses(company_type=None,file_name='companies.csv'):
    if not company_type or company_type not in(TblCompany.COMPANY_TYPE_ENTAJ,TblCompany.COMPANY_TYPE_EMTIAZ,TblCompany.COMPANY_TYPE_MOKHALFAT,TblCompany.COMPANY_TYPE_SAGEER):
        print('Please pass correct company type!')
        return
    
    with open('./company_profile/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            name_ar = row[0].strip()
            name_en = row[1].strip()
            nationality_str = row[2].strip()
            address = row[3].strip()
            website = row[4].strip()
            manager_name = row[5]
            manager_phone = row[6]
            rep_name = row[7].strip()
            rep_phone = row[8]
            email = row[9]
            status_str = row[10]

            nationality, created = LkpNationality.objects.get_or_create(name=nationality_str)
            status, created = LkpCompanyProductionStatus.objects.get_or_create(name=status_str)

            try:
                company = TblCompanyProduction.objects.create(
                    company_type=company_type,
                    name_ar=name_ar,
                    name_en=name_en,
                    address=address,
                    website=website,
                    manager_name=manager_name,
                    manager_phone=manager_phone,
                    rep_name=rep_name,
                    rep_phone=rep_phone,
                    email=email,
                    status=status,  
                    created_by=admin_user,
                    updated_by=admin_user
                )
                company.nationality.set([nationality])
            except Exception as e:
                print(f'name_ar: {name_ar}, name_en: {name_en}, Exception: {e}')

