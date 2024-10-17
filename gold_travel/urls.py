from django.urls import path

from django.conf import settings

from .views import WhomMayConcern


app_name = "gold_travel"
urlpatterns = [                                                        
    path('certificate/whom_may_concern', WhomMayConcern.as_view(), name='whom_may_concern'),

]