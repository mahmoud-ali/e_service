from workflow.data_utils import create_master_details_groups
from hse_traditional import admin

def create_groups():
    create_master_details_groups('hse_traditional','hsetraditionalreport',admin.report_main_class,admin.report_inline_classes)
    create_master_details_groups('hse_traditional','hsetraditionalaccident',admin.accident_main_class,admin.accident_inline_classes)
    create_master_details_groups('hse_traditional','hsetraditionalnearmiss',admin.near_miss_main_class,admin.near_miss_inline_classes)
    create_master_details_groups('hse_traditional','hsetraditionalcorrectiveaction',admin.corrective_action_main_class,admin.corrective_action_inline_classes)

if __name__ == '__main__':
    create_groups()
    