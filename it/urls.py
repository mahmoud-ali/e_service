from django.urls import path

from it.views import (
    EmployeeComputerAskAIView,
    HelpdeskTelegramUser,
    ManagerDashboardView,
    ManagerHelpRequestListView,
    ManagerHelpRequestDetailView,
    ManagerHelpRequestUpdateView,
    ManagerEmployeeComputerListView,
    ManagerEmployeeComputerDetailView,
)

app_name = "it"
urlpatterns = [
    path('ai/<int:pk>/', EmployeeComputerAskAIView.as_view(), name='ai_prompt'),
    path('help_desk_form/<uuid:user_id>/', HelpdeskTelegramUser.as_view(), name='help_desk_form'),

    # Manager Portal URLs
    path('manager/', ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('manager/help-requests/', ManagerHelpRequestListView.as_view(), name='manager_help_request_list'),
    path('manager/help-requests/<uuid:pk>/', ManagerHelpRequestDetailView.as_view(), name='manager_help_request_detail'),
    path('manager/help-requests/<uuid:pk>/update/', ManagerHelpRequestUpdateView.as_view(), name='manager_help_request_update'),
    path('manager/computers/', ManagerEmployeeComputerListView.as_view(), name='manager_employee_computer_list'),
    path('manager/computers/<int:pk>/', ManagerEmployeeComputerDetailView.as_view(), name='manager_employee_computer_detail'),
]
