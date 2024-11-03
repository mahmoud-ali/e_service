import csv

from django.contrib.auth import get_user_model

from ..models import AppMoveGold

admin_user = get_user_model().objects.get(id=1)

def import_history(file_name='history.csv'):
    with open('./gold_travel/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                license_id = int(row[0].strip())
                
                move = AppMoveGold.objects.create(

                )

            except Exception as e:
                print(f"id: {id}")