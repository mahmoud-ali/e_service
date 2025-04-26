import csv
import datetime

from django.contrib.auth import get_user_model

from company_profile.models import LkpState

from ..models import AppDabtiaat

admin_user = get_user_model().objects.get(id=1)

def import_history(file_name='g_import.csv'):
    # date_format = '%d/%m/%Y'
    with open('./dabtiaat_altaedin/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                state_id = row[0].strip()
                weight = row[1].strip()
                price = row[2].strip()
                date = '2025-01-31'
                # date = datetime.datetime.strptime(date, date_format)
                source_state=LkpState.objects.get(pk=state_id)
                AppDabtiaat.objects.create(date=date,gold_weight_in_gram=weight,gold_price=price,source_state=source_state,state=2,created_by=admin_user,updated_by=admin_user)
            except Exception as e:
                print(f"id: {id}, Exception: {e}")

def migrate_master_to_details():
    qs = AppDabtiaat.objects.all()
    for obj in qs:
        obj.appdabtiaatdetails_set.create(gold_weight_in_gram=obj.gold_weight_in_gram,gold_price=obj.gold_price,gold_caliber=obj.gold_caliber)