from django.urls import path

from traditional_app.views import PayrollT3agood, geojson_soug_view
from traditional_app.portal_views import (
    DashboardView, DailyReportsListView, DailyReportDetailView,
    DailyReportTransitionView, EmployeesListView, EmployeeDetailView,
    PayrollListView, PayrollDetailView, ProfileView, SettingsView
)

app_name = "traditional_app"
urlpatterns = [
    # Existing URLs
    path('payroll_t3agood/', PayrollT3agood.as_view(), name='payroll_t3agood'),
    path('soug_layer/', geojson_soug_view, name='soug_layer'),
    
    # Portal URLs
    path('portal/', DashboardView.as_view(), name='portal_dashboard'),
    path('portal/profile/', ProfileView.as_view(), name='portal_profile'),
    path('portal/settings/', SettingsView.as_view(), name='portal_settings'),
    
    # Daily Reports
    path('portal/daily-reports/', DailyReportsListView.as_view(), name='portal_daily_reports'),
    path('portal/daily-reports/<int:pk>/', DailyReportDetailView.as_view(), name='portal_daily_report_detail'),
    path('portal/daily-reports/<int:pk>/transition/', DailyReportTransitionView.as_view(), name='portal_daily_report_transition'),
    
    # Employees
    path('portal/employees/', EmployeesListView.as_view(), name='portal_employees'),
    path('portal/employees/<int:pk>/', EmployeeDetailView.as_view(), name='portal_employee_detail'),
    
    # Payroll
    path('portal/payroll/', PayrollListView.as_view(), name='portal_payroll'),
    path('portal/payroll/<int:pk>/', PayrollDetailView.as_view(), name='portal_payroll_detail'),
]
