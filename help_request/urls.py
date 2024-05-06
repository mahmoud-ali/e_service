from django.urls import path

from help_request.views import HelpView

app_name = "help_request"
urlpatterns = [                                                        
    path('', HelpView.as_view(), name='help'),
]