import csv

from django.contrib.auth import get_user_model

from ..models import LkpCompanyProductionLicenseStatus, LkpCompanyProductionStatus, LkpLocality, LkpMineral, LkpNationality, LkpState, TblCompany, TblCompanyProduction, TblCompanyProductionLicense
# from company_profile.models import LkpNationality,TblCompanyProduction

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

def import_licenses_entaj(file_name='licenses_entaj.csv'):
    with open('./company_profile/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:

                id = int(row[1].strip())
                license_no = row[2].strip()
                date = row[3].strip()
                start_date = row[4].strip()
                end_date = row[5].strip()
                state_str = row[6].strip()
                locality_str = row[7].strip()
                location = row[8].strip()
                sheet_no = row[9].strip()
                mineral_str = row[10].strip()
                area = float(row[11].strip())
                reserve = float(row[12].strip())
                gov_rep = float(row[13].strip())
                rep_percent = float(row[14].strip())
                com_percent = float(row[15].strip())
                royalty = float(row[16].strip())
                zakat = float(row[17].strip())
                annual_rent = float(row[18].strip())
                contract_status_str = row[19].strip()

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
                    contract_status = contract_status,
                    created_by=admin_user,
                    updated_by=admin_user
                )
                license.mineral.set([mineral])
            except Exception as e:
                print(f'id: {id} Exception: {e}')

def import_licenses_mokhalafat(file_name='licenses_mokhalafat_remain.csv'):
    with open('./company_profile/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:

                id = int(row[0].strip())
                license_no = row[2].strip()
                date = row[3].strip()
                start_date = row[4].strip()
                end_date = row[5].strip()
                state_str = row[6].strip()
                locality_str = row[7].strip()
                location = row[8].strip()
                sheet_no = row[9].strip()
                mineral_str = row[10].strip()
                area = float(row[11].strip())
                area_initial = float(row[11].strip())
                royalty = float(row[16].strip())
                business_profit = float(row[17].strip())
                social_responsibility = float(row[18].strip())
                zakat = 2.5
                contract_status_str = row[21].strip()

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
                    area_initial = area_initial,
                    royalty = royalty,
                    zakat = zakat,
                    business_profit = business_profit,
                    social_responsibility = social_responsibility,
                    contract_status = contract_status,
                    created_by=admin_user,
                    updated_by=admin_user
                )
                license.mineral.set([mineral])
            except Exception as e:
                print(f'id: {id} Exception: {e}')

def import_licenses_mokhalafat_hajr(file_name='licenses_hajar.csv'):
    with open('./company_profile/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:

                id = int(row[1].strip())
                license_no = id

                license = TblCompanyProductionLicense.objects.get(license_no=id)
                license.license_no = str(license_no) +' / حجر'
                license.pk = None
                license.save()
            except Exception as e:
                print(f'id: {id} Exception: {e}')


def import_licenses_emtiaz(file_name='licenses_emtiaz.csv'):
    with open('./company_profile/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:

                id = int(row[0].strip())
                license_no = row[2].strip()
                date = row[3].strip()
                start_date = row[4].strip()
                end_date = row[5].strip()
                state_str = row[6].strip()
                locality_str = row[7].strip()
                location = row[8].strip()
                sheet_no = row[9].strip()
                mineral_str = row[10].strip()
                area = float(row[11].strip())
                reserve = 0
                gov_rep = 'وزارة المعادن'
                rep_percent = float(row[12].strip())
                com_percent = 0
                royalty = 0
                business_profit = 0
                social_responsibility = 0
                zakat = 2.5
                annual_rent = float(row[14].strip())
                contract_status_str = row[15].strip()

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
                print(f'id: {id} Exception: {e}')

def update_intial_area():
    for obj in TblCompanyProductionLicense.objects.all():
        obj.area_initial = obj.area
        obj.save()

def import_licenses_emtiaz_update_initial_area(file_name='licenses_emtiaz.csv'):
    with open('./company_profile/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:

                id = int(row[0].strip())
                license_no = row[2].strip()
                initial_area = float(row[17].strip())

                license = TblCompanyProductionLicense.objects.get(company__id=id,license_no=license_no)
                license.area_initial = initial_area
                license.save()
            except Exception as e:
                print(f'id: {id} Exception: {e}')

def import_licenses_sageer(file_name='licenses_sageer.csv'):
    with open('./company_profile/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:

                id = int(row[0].strip())
                license_no = row[2].strip()
                date = row[3].strip()
                start_date = row[4].strip()
                end_date = row[5].strip()
                state_str = row[6].strip()
                locality_str = row[7].strip()
                location = row[8].strip()
                sheet_no = row[9].strip()
                mineral_str = row[10].strip()
                area = float(row[11].strip())
                reserve = float(row[12].strip())
                gov_rep = float(row[13].strip())
                rep_percent = float(row[14].strip())
                com_percent = float(row[15].strip())
                royalty = float(row[16].strip())
                zakat = float(row[17].strip())
                annual_rent = float(row[18].strip())
                contract_status_str = row[19].strip()

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
                    area_initial = area,
                    reserve = reserve,
                    gov_rep = gov_rep,
                    rep_percent = rep_percent,
                    com_percent = com_percent,
                    royalty = royalty,
                    zakat = zakat,
                    annual_rent = annual_rent,
                    contract_status = contract_status,
                    created_by=admin_user,
                    updated_by=admin_user
                )
                license.mineral.set([mineral])
            except Exception as e:
                print(f'id: {id} Exception: {e}')

# from company_profile.models import LkpNationality,TblCompanyProduction

def update_nationality(r,a):
    nat_r = LkpNationality.objects.get(id=r)
    nat_a = LkpNationality.objects.get(id=a)
    lst = TblCompanyProduction.objects.filter(nationality=nat_r)
    for obj in lst:
        obj.nationality.remove(nat_r)
        obj.nationality.add(nat_a)
        obj.save()

def update_emtiaz_nasib():
    data = (
        (15,[437,441,450,454,460,461,463,468]),
        (18,[479,509,510]),
        (20,[428,429,431,433,447,474,499,565]),
        (22,[434,436,472,477]),
        (23,[443]),
        (25,[412,414,416,417,418,419,421,427,432,438,439,440,442,448,457,475,489,494,508,563]),
        (27,[425,476]),
        (30,[420,423,424,426,430,444,445,446,449,451,452,453,458,464,466,467,469,470,471,473,481,482,483,484,485,486,487,488,490,491,492,493,495,496,497,498,500,501,502,503,504,505,506,507,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,564,566,567,568,569,570,571]),
        (35,[413,415,435,455,456,459,465]),
        (45,[478]),
    )    
    for row in data:
        for company_id in row[1]:
            nasib_gov = row[0]
            nasib_com = 100 - nasib_gov
            try:
                obj = TblCompanyProductionLicense.objects.get(company__id=company_id,company__company_type='emtiaz')
                obj.rep_percent = nasib_gov
                obj.com_percent = nasib_com
                obj.save()
            except Exception as e:
                print(f'id: {company_id} Exception: {e}')