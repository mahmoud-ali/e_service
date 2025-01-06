from django.urls import path

from django.conf import settings

from .views import ShippingView


app_name = "production"
urlpatterns = [                                                        
    path('shipping', ShippingView, name='production_shipping'),

]