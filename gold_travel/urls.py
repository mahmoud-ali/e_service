from django.urls import path

from django.conf import settings

from .views import GoldTravelCert, WhomMayConcern


app_name = "gold_travel"
urlpatterns = [                                                        
    path('certificate/gold_travel', GoldTravelCert.as_view(), name='gold_travel_cert'),
    path('certificate/whom_may_concern', WhomMayConcern.as_view(), name='whom_may_concern'),

]