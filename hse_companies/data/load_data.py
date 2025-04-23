from workflow.data_utils import create_master_details_groups
from hse_companies import admin

def create_groups():
    create_master_details_groups('hse_companies','apphseperformancereport',admin.report_main_class,admin.report_inline_classes)
    create_master_details_groups('hse_companies','apphsecorrectiveaction',admin.corrective_main_class,admin.corrective_inline_classes)
    create_master_details_groups('hse_companies','apphsecorrectiveactionfeedback',admin.corrective_action_feedback_main_class,admin.corrective_action_feedback_inline_classes)

if __name__ == '__main__':
    create_groups()
    