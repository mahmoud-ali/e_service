from django.urls import path
from . import views

app_name = 'fleet'

urlpatterns = [
    path('', views.portal_home, name='portal_home'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/<int:pk>/', views.driver_detail, name='driver_detail'),
    path('missions/', views.mission_list, name='mission_list'),
    path('missions/<int:pk>/', views.mission_detail, name='mission_detail'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/<int:pk>/', views.maintenance_detail, name='maintenance_detail'),
]
