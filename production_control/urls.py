from django.urls import path, include

from django.conf import settings
from rest_framework.authtoken import views
from .views import ProductionView, ShippingView, Auth


app_name = "production"
urlpatterns = [                                                        
    path('auth', include('rest_framework_simplejwt.urls')),
    path('production', ProductionView, name='production_production'),
    path('shipping', ShippingView, name='production_shipping'),

]