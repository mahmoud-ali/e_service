from django.urls import path
from . import views
app_name = "surveys"
urlpatterns = [
    path("emergency_survey/", views.emergency_form, name="emergency_form"),
    path('get_employee_name/', views.get_employees_under_manager, name='get_employees_under_manager'),
    path('structure_survey/', views.survey_view, name='survey_form'),
    path('survey_thank_you/', views.survey_thank_you, name='survey_thank_you'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('create_employee/', views.employee_create, name='employee_create'),
    path('list/', views.survey_list_view, name='survey_list'), 
    path('submissions/', views.submission_list_view, name='submission_list'),
    
]
