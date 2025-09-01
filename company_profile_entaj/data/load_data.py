import csv
import datetime

from django.contrib.auth.models import Group, Permission

from django.contrib.auth import get_user_model

from workflow.data_utils import create_master_details_groups
from company_profile_entaj import admin

admin_user = get_user_model().objects.get(id=1)

# def create_groups():
#     group, created = Group.objects.get_or_create(name="exploration_technical_development")
#     group, created = Group.objects.get_or_create(name="exploration_technical_exploration")
#     # group, created = Group.objects.get_or_create(name="exploration_secretary")

#     create_master_details_groups('company_profile_exploration','appworkplan',admin.work_plan_main_class,admin.work_plan_inline_classes)

def import_history(file_name='rn_import.csv'):
    date_format = '%d/%m/%Y'
    with open('./company_profile_entaj/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                pass

            except Exception as e:
                print(f"id: {id}, Exception: {e}")
