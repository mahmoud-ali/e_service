import csv

from django.contrib.auth import get_user_model

from ..models.performance_report import AppHSEPerformanceReport

from workflow.data_utils import create_master_details_groups
from hse_companies import admin

def create_groups():
    create_master_details_groups('hse_companies','apphseperformancereport',admin.report_main_class,admin.report_inline_classes)
    create_master_details_groups('hse_companies','incidentinfo',admin.incident_main_class,admin.incident_inline_classes)
    create_master_details_groups('hse_companies','apphsecorrectiveaction',admin.corrective_main_class,admin.corrective_inline_classes)
    create_master_details_groups('hse_companies','apphsecorrectiveactionfeedback',admin.corrective_action_feedback_main_class,admin.corrective_action_feedback_inline_classes)
    
admin_user = get_user_model().objects.get(id=1)

def update_year_month(file_name='update_year_month.csv'):
    with open('./hse_companies/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                id = int(row[0].strip())
                year = int(row[1].strip())
                month = int(row[2].strip())

                report = AppHSEPerformanceReport.objects.get(id=id)
                report.year = year
                report.month = month

                report.save()
            except Exception as e:
                print(f"Error: id: {id}, year:{year}, month:{month}, {e}")
