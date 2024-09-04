from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from . import views


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
app_name = "traditional_api"

urlpatterns = [
    path('lkp_soag/<int:master_id>/<int:dependent_id>/', views.LkpSoagSelectView.as_view(), name='lkp_soag_select'),
    path('login/', views.AuthView.as_view(), name='login'), 
    path('invoice/', views.InvoiceView.as_view(), name='invoice'), 
]