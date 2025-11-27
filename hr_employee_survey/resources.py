from import_export import resources
from hr_employee_survey.models import  Employee_Data_Emergency          

class DataResource(resources.ModelResource):
    class Meta:
        model = Employee_Data_Emergency
