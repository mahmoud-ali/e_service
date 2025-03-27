from django.contrib.auth.models import Group, Permission

from workflow.data_utils import create_master_details_groups
from company_profile_exploration import admin

def create_groups():
    group, created = Group.objects.get_or_create(name="exploration_technical_development")
    group, created = Group.objects.get_or_create(name="exploration_technical_exploration")
    # group, created = Group.objects.get_or_create(name="exploration_secretary")

    create_master_details_groups('company_profile_exploration','appworkplan',admin.work_plan_main_class,admin.work_plan_inline_classes)

if __name__ == '__main__':
    create_groups()