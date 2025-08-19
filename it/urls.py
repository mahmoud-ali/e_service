from django.urls import path

from it.views import EmployeeComputerAskAIView, HelpdeskTelegramUser

app_name = "it"
urlpatterns = [      
    path('ai/<int:pk>/', EmployeeComputerAskAIView.as_view(), name='ai_prompt'),
    path('help_desk_form/<uuid:user_id>/', HelpdeskTelegramUser.as_view(), name='help_desk_form'),
]