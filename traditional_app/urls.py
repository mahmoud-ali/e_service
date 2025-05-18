from django.urls import path

from traditional_app.views import PayrollT3agood

app_name = "traditional_app"
urlpatterns = [                                                        
    path('payroll_t3agood/', PayrollT3agood.as_view(), name='payroll_t3agood'),
]