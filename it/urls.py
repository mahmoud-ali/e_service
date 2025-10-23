from django.urls import path

from it.views import EmployeeComputerAskAIView, HelpdeskTelegramUser
from it.portal_views import PortalDashboard, HelpRequestCreateView, ComputerDetailView

app_name = "it"
urlpatterns = [      
    path('ai/<int:pk>/', EmployeeComputerAskAIView.as_view(), name='ai_prompt'),
    path('help_desk_form/<uuid:user_id>/', HelpdeskTelegramUser.as_view(), name='help_desk_form'),
    path('portal/', PortalDashboard.as_view(), name='portal_dashboard'),
    path('portal/help-request/', HelpRequestCreateView.as_view(), name='portal_help_request'),
    path('portal/computer/<int:pk>/', ComputerDetailView.as_view(), name='portal_computer_detail'),
]
