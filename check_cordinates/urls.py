from django.urls import path
from .views import CheckCordinatesView

app_name = "check_cordinates"
urlpatterns = [                                                        
    path('', CheckCordinatesView.as_view(), name='check_view'),
]