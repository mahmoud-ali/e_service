import csv
from datetime import date

from django.contrib.auth import get_user_model

from datetime import date
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

def import_commitment_exp(file_name='commitment_exp.csv',items=['أخرى/تسوية','بونص توقيع إتفاقية الإمتياز','ممثل حكومة','دعم فني','إيجار ارض لإتفاقيات الإمتياز']):
    with open('./pa/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                license_id = int(row[0].strip())
                license = TblCompanyProductionLicense.objects.get(pk=license_id)
                currency_str = row[9].strip()
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
                    item,created = LkpItem.objects.get_or_create(name=v+' (قيمة محددة)',company_type=TblCompany.COMPANY_TYPE_EMTIAZ,calculation_method=LkpItem.CALCULATION_METHOD_FIXED_VALUE)
                    try:
                        amount = float(row[11+i].strip())
                    except:
                        amount = 0

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

def remove_request_with_zero_total():
    for request in TblCompanyRequestMaster.objects.all():
        if request.total == 0:
            print("request will be deleted:",request.id)
            request.tblcompanyrequestdetail_set.all().delete()
            request.delete()
        else:
            for obj in request.tblcompanyrequestdetail_set.all():
                if obj.amount == 0:
                    print("request detail of request:",request.id," will be deleted:",obj.id)
                    obj.delete()

def remove_mokhalafat_requests():
    for request in TblCompanyRequestMaster.objects.filter(commitment__company__company_type=TblCompany.COMPANY_TYPE_MOKHALFAT):
        print("request will be deleted:",request.id)
        request.tblcompanyrequestdetail_set.all().delete()
        request.commitment.tblcompanycommitmentdetail_set.all().delete()
        commitment = request.commitment
        request.delete()
        commitment.delete()

def import_mokhalafat_request(file_name='request_mokhalafat.csv',currency="sdg"):
    with open('./pa/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                license_id = int(row[0].strip())
                license = TblCompanyProductionLicense.objects.get(pk=license_id)
                hajr = int(row[2].strip())
                if currency=="sdg":
                    amount = float(row[3].strip())
                else:
                    amount = float(row[4].strip())

                if amount == 0:
                    continue
                
                if hajr == 0:
                    items = ['رسوم تجديد عقد معالجة المخلفات','بونص توقيع عقد المخلفات']
                else:
                    items = ['رسوم العقد الثلاثي','بونص العقد الثلاثي']
                
                commitmentMaster = TblCompanyCommitmentMaster.objects.create(
                    company=license.company,
                    license=license,
                    currency=currency,
                    state=STATE_TYPE_CONFIRM,
                    note='التزام بمتبقي الرصيد حتى 31/12/2024 لاغراض التصدير',
                    created_by=admin_user,
                    updated_by=admin_user
                )

                requestMaster = TblCompanyRequestMaster.objects.create(
                    commitment=commitmentMaster,
                    from_dt=date(2024, 1, 1),
                    to_dt=date(2024, 12, 31),
                    currency=currency,
                    payment_state=TblCompanyRequestMaster.REQUEST_PAYMENT_NO_PAYMENT,
                    state=STATE_TYPE_DRAFT,
                    note='مطالبة بمتبقي الرصيد حتى 31/12/2024 لاغراض التصدير',
                    created_by=admin_user,
                    updated_by=admin_user
                )

                for i,item_name in enumerate(items):
                    item,created = LkpItem.objects.get_or_create(name=item_name+' (قيمة محددة)',company_type=TblCompany.COMPANY_TYPE_MOKHALFAT,calculation_method=LkpItem.CALCULATION_METHOD_FIXED_VALUE)
                    
                    TblCompanyCommitmentDetail.objects.create(
                        commitment_master=commitmentMaster,
                        item=item,
                        amount_factor=0,
                    )
                    
                    if i == 0:
                        x_amount = amount
                    else:
                        x_amount = 0

                    TblCompanyRequestDetail.objects.create(
                        request_master=requestMaster,
                        item=item,
                        amount=x_amount,
                    )
            except Exception as e:
                print(f'id: {license_id} Exception: {e}')


