import csv

from django.contrib.auth import get_user_model

from ..models import LkpCompanyProductionLicenseStatus, LkpCompanyProductionStatus, LkpLocality, LkpMineral, LkpNationality, LkpState, TblCompany, TblCompanyProduction, TblCompanyProductionLicense

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

def import_licenses(file_name='licenses_mokhalafat.csv'):
    with open('./company_profile/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:

                id = int(row[1].strip())
                license_no = id
                date = row[2].strip()
                start_date = row[3].strip()
                end_date = row[4].strip()
                state_str = row[5].strip()
                locality_str = row[6].strip()
                location = row[7].strip()
                sheet_no = row[8].strip()
                mineral_str = row[9].strip()
                area = float(row[10].strip())
                reserve = float(row[11].strip())
                gov_rep = float(row[12].strip())
                rep_percent = float(row[13].strip())
                com_percent = float(row[14].strip())
                royalty = float(row[15].strip())
                business_profit = float(row[16].strip())
                social_responsibility = float(row[17].strip())
                zakat = float(row[18].strip())
                annual_rent = float(row[19].strip())
                contract_status_str = row[20].strip()

                company = TblCompanyProduction.objects.get(id=id)
                state, created = LkpState.objects.get_or_create(name=state_str)
                locality, created = LkpLocality.objects.get_or_create(name=locality_str,state=state)
                mineral, created = LkpMineral.objects.get_or_create(name=mineral_str)
                contract_status, created = LkpCompanyProductionLicenseStatus.objects.get_or_create(name=contract_status_str)

                license = TblCompanyProductionLicense.objects.create(
                    company = company,
                    license_no = license_no,
                    date = date,
                    start_date = start_date,
                    end_date = end_date,
                    state = state,
                    locality = locality,
                    location = location,
                    sheet_no = sheet_no,
                    area = area,
                    reserve = reserve,
                    gov_rep = gov_rep,
                    rep_percent = rep_percent,
                    com_percent = com_percent,
                    royalty = royalty,
                    zakat = zakat,
                    annual_rent = annual_rent,
                    business_profit = business_profit,
                    social_responsibility = social_responsibility,
                    contract_status = contract_status,
                    created_by=admin_user,
                    updated_by=admin_user
                )
                license.mineral.set([mineral])
            except Exception as e:
                print(f'id: {id}, company: {company} Exception: {e}')

