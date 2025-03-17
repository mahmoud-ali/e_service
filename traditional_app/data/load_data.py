from workflow.data_utils import create_master_details_groups
from traditional_app import admin

def create_groups():
    create_master_details_groups('traditional_app','dailyreport',admin.daily_report_main_class,admin.daily_report_inline_classes)

if __name__ == '__main__':
    create_groups()