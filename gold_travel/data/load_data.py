import csv
import datetime

from django.contrib.auth import get_user_model

from company_profile.models import LkpState

from ..models import AppMoveGold, AppMoveGoldDetails, LkpOwner

admin_user = get_user_model().objects.get(id=1)

def import_history(file_name='rn_import.csv'):
    date_format = '%d/%m/%Y'
    with open('./gold_travel/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                code = row[0].strip()
                date_str = row[2].strip()
                date = datetime.datetime.strptime(date_str, date_format)
                owner_name_lst = LkpOwner.objects.get(pk=int(row[5].strip()))
                source_state=LkpState.objects.get(pk=1)

                alloy_weight_in_gram = float(row[3].strip())
                
                move = AppMoveGold.objects.create(
                    code=code,
                    date=date,
                    owner_name_lst=owner_name_lst,
                    owner_address='-',
                    repr_name='-',
                    repr_address='-',
                    repr_phone='-',
                    repr_identity_type=1,
                    repr_identity='-',
                    repr_identity_issue_date=datetime.date(2000,12,31),
                    state=6,
                    source_state=source_state,
                    created_by=admin_user,
                    updated_by=admin_user
                )

                AppMoveGoldDetails.objects.create(
                    master=move,
                    alloy_id="1",
                    alloy_weight_in_gram=alloy_weight_in_gram,
                    alloy_shape=1,
                    alloy_note='تصدير',
                )

            except Exception as e:
                print(f"id: {id}, Exception: {e}")