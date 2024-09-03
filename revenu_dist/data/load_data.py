import csv

from django.contrib.auth import get_user_model

from ..models import LkpRevenu,LkpRevenuType

admin_user = get_user_model().objects.get(id=1)

def import_revenu(file_name='revenu.csv'):
    with open('./revenu_dist/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            name = row[0].strip()
            type_id = int(row[1].strip())

            try:
                revenu_type = LkpRevenuType.objects.get(id=type_id)

                revenu = LkpRevenu.objects.create(
                    name=name,
                    revenu_type=revenu_type,
                )
            except Exception as e:
                print(f'name: {name}, revenu_type: {type}, Exception: {e}')
