from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from . import views


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('bok/inquiry/', views.InqueryView.as_view()),
    path('bok/payment/', views.PaymentView.as_view()),
    path('api-token-auth/', obtain_auth_token) #post username & password to get token
    # path('auth/', include('djoser.urls'))
]