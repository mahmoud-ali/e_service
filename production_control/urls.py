from django.urls import path

from django.conf import settings

from .views import ProductionView, ShippingView


app_name = "production"
urlpatterns = [                                                        
    path('production', ProductionView, name='production_production'),
    path('shipping', ShippingView, name='production_shipping'),

]