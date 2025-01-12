from django.urls import path

from django.conf import settings

from .views import ProductionView, ShippingView, Auth


app_name = "production"
urlpatterns = [                                                        
    path('auth', Auth, name='production_production'),
    path('production', ProductionView, name='production_production'),
    path('shipping', ShippingView, name='production_shipping'),

]