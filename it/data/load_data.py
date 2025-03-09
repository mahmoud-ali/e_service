from workflow.data_utils import create_master_details_groups
from it import admin

def create_groups():
    create_master_details_groups('it','developmentrequestform',admin.development_request_main_class,admin.development_request_inline_classes)
    create_master_details_groups('it','itservice',admin.it_service_main_class,admin.it_service_inline_classes)

if __name__ == '__main__':
    create_groups()