from django.urls import path

from it.views import EmployeeComputerAskAIView

app_name = "it"
urlpatterns = [      
    path('ai/<int:pk>/', EmployeeComputerAskAIView.as_view(), name='ai_prompt'),
]