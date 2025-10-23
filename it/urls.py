from django.urls import path

from it.views import EmployeeComputerAskAIView, HelpdeskTelegramUser
from it.views_portal import HelpRequestListView

app_name = "it"
urlpatterns = [      
    path('ai/<int:pk>/', EmployeeComputerAskAIView.as_view(), name='ai_prompt'),
    path('help_desk_form/<uuid:user_id>/', HelpdeskTelegramUser.as_view(), name='help_desk_form'),
    # Portal URLs
    path('portal/', HelpRequestListView.as_view(), name='portal_help_request_list'),
]
