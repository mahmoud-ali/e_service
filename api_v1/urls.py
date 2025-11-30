from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from . import views


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('auth/', obtain_auth_token),
    path('gold_travel_list/<str:date>/', views.GoldTravelListView.as_view()),
    path('gold_travel_retrieve/<int:pk>/', views.GoldTravelDetailView.as_view()),
    path('gold_production_list/<str:date>/', views.GoldProductionListView.as_view()),
    path('gold_production_retrieve/<int:pk>/', views.GoldProductionDetailView.as_view()),
    path('gold_shipping_list/<str:date>/', views.GoldShippingListView.as_view()),
    path('gold_shipping_retrieve/<int:pk>/', views.GoldShippingDetailView.as_view()),
]