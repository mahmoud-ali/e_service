import csv

from django.contrib.auth import get_user_model

from company_profile.models import TblCompany

from django.conf import settings

from production_control.models import LkpMoragib
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
        for row in reader:
            try:
                code = row[0].strip()
                name = row[1].strip()
                email = row[2].strip()

                user = User.objects.create_user(email, email, settings.ACCOUNT_DEFAULT_PASSWORD)
                
                moragib = LkpMoragib.objects.create(
                    user=user,
                    name=name,
                    emp_code=code,
                    company_type=company_type,
                )

                print(f"Created successfully, user: {user}, moragib: {moragib}")

            except Exception as e:
                print(f"id: {code}, Exception: {e}")
