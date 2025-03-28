from django.urls import path, include

from django.conf import settings
from rest_framework.authtoken import views
from .views import ProductionCert, ProductionView, ShippingCert, ShippingView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = "production"
urlpatterns = [                           
    path('certificate/production/', ProductionCert.as_view(), name='production_certificate'),
    path('certificate/shipping/', ShippingCert.as_view(), name='shipping_certificate'),
    path('auth/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
    path('production/<str:from_dt>/<str:to_dt>/', ProductionView, name='production_production'),
    path('shipping/<str:from_dt>/<str:to_dt>/', ShippingView, name='production_shipping'),

]