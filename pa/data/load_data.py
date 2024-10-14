import csv

from django.contrib.auth import get_user_model

from ..models import STATE_TYPE_CONFIRM, STATE_TYPE_DRAFT, LkpItem,TblCompany, TblCompanyCommitmentDetail, TblCompanyProduction, TblCompanyProductionLicense,TblCompanyCommitmentMaster, TblCompanyRequestDetail, TblCompanyRequestMaster
# from company_profile.models import LkpNationality,TblCompanyProduction

admin_user = get_user_model().objects.get(id=1)

currency_map = {
    'جنيه': 'sdg',
    'دولار': 'dollar',
    'يورو': 'euro',
}

def import_commitment_mokhalafat(file_name='commitment_mokhalafat.csv',items=['متبقي رسوم عقد المخلفات']):
    with open('./pa/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                license_id = int(row[0].strip())
                license = TblCompanyProductionLicense.objects.get(pk=license_id)
                currency_str = row[5].strip()
                currency = currency_map[currency_str]
                
                commitmentMaster = TblCompanyCommitmentMaster.objects.create(
                    company=license.company,
                    license=license,
                    currency=currency,
                    state=STATE_TYPE_CONFIRM,
                    note='التزام بمتبقي الرصيد لاغراض التصدير',
                    created_by=admin_user,
                    updated_by=admin_user
                )

                requestMaster = TblCompanyRequestMaster.objects.create(
                    commitment=commitmentMaster,
                    from_dt=license.start_date,
                    to_dt=license.end_date,
                    currency=currency,
                    payment_state=TblCompanyRequestMaster.REQUEST_PAYMENT_NO_PAYMENT,
                    state=STATE_TYPE_DRAFT,
                    note='مطالبة بمتبقي الرصيد لاغراض التصدير',
                    created_by=admin_user,
                    updated_by=admin_user
                )

                for (i,v) in enumerate(items):
                    item,created = LkpItem.objects.get_or_create(name=v+' (قيمة محددة)',company_type=TblCompany.COMPANY_TYPE_MOKHALFAT,calculation_method=LkpItem.CALCULATION_METHOD_FIXED_VALUE)
                    amount = float(row[6+i].strip())

                    commitmentDetail = TblCompanyCommitmentDetail.objects.create(
                        commitment_master=commitmentMaster,
                        item=item,
                        amount_factor=0,
                    )
                    
                    requestDetail = TblCompanyRequestDetail.objects.create(
                        request_master=requestMaster,
                        item=item,
                        amount=amount,
                    )
            except Exception as e:
                print(f'id: {license_id} Exception: {e}')

def import_commitment_emtiaz(file_name='commitment_emtiaz.csv',items=['عقود تعدين']):
    with open('./pa/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                license_id = int(row[0].strip())
                license = TblCompanyProductionLicense.objects.get(pk=license_id)
                currency_str = row[5].strip()
                currency = currency_map[currency_str]
                
                commitmentMaster = TblCompanyCommitmentMaster.objects.create(
                    company=license.company,
                    license=license,
                    currency=currency,
                    state=STATE_TYPE_CONFIRM,
                    note='التزام بمتبقي الرصيد لاغراض التصدير',
                    created_by=admin_user,
                    updated_by=admin_user
                )

                requestMaster = TblCompanyRequestMaster.objects.create(
                    commitment=commitmentMaster,
                    from_dt=license.start_date,
                    to_dt=license.end_date,
                    currency=currency,
                    payment_state=TblCompanyRequestMaster.REQUEST_PAYMENT_NO_PAYMENT,
                    state=STATE_TYPE_DRAFT,
                    note='مطالبة بمتبقي الرصيد لاغراض التصدير',
                    created_by=admin_user,
                    updated_by=admin_user
                )

                for (i,v) in enumerate(items):
                    item,created = LkpItem.objects.get_or_create(name=v+' (قيمة محددة)',company_type=TblCompany.COMPANY_TYPE_ENTAJ,calculation_method=LkpItem.CALCULATION_METHOD_FIXED_VALUE)
                    amount = float(row[7+i].strip())

                    commitmentDetail = TblCompanyCommitmentDetail.objects.create(
                        commitment_master=commitmentMaster,
                        item=item,
                        amount_factor=0,
                    )
                    
                    requestDetail = TblCompanyRequestDetail.objects.create(
                        request_master=requestMaster,
                        item=item,
                        amount=amount,
                    )
            except Exception as e:
                print(f'id: {license_id} Exception: {e}')

def import_commitment_sageer(file_name='commitment_sageer.csv',items=['اجار']):
    with open('./pa/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                license_id = int(row[0].strip())
                license = TblCompanyProductionLicense.objects.get(pk=license_id)
                currency_str = row[5].strip()
                currency = currency_map[currency_str]
                
                commitmentMaster = TblCompanyCommitmentMaster.objects.create(
                    company=license.company,
                    license=license,
                    currency=currency,
                    state=STATE_TYPE_CONFIRM,
                    note='التزام بمتبقي الرصيد لاغراض التصدير',
                    created_by=admin_user,
                    updated_by=admin_user
                )

                requestMaster = TblCompanyRequestMaster.objects.create(
                    commitment=commitmentMaster,
                    from_dt=license.start_date,
                    to_dt=license.end_date,
                    currency=currency,
                    payment_state=TblCompanyRequestMaster.REQUEST_PAYMENT_NO_PAYMENT,
                    state=STATE_TYPE_DRAFT,
                    note='مطالبة بمتبقي الرصيد لاغراض التصدير',
                    created_by=admin_user,
                    updated_by=admin_user
                )

                for (i,v) in enumerate(items):
                    item,created = LkpItem.objects.get_or_create(name=v+' (قيمة محددة)',company_type=TblCompany.COMPANY_TYPE_SAGEER,calculation_method=LkpItem.CALCULATION_METHOD_FIXED_VALUE)
                    amount = float(row[6+i].strip())

                    commitmentDetail = TblCompanyCommitmentDetail.objects.create(
                        commitment_master=commitmentMaster,
                        item=item,
                        amount_factor=0,
                    )
                    
                    requestDetail = TblCompanyRequestDetail.objects.create(
                        request_master=requestMaster,
                        item=item,
                        amount=amount,
                    )
            except Exception as e:
                print(f'id: {license_id} Exception: {e}')

