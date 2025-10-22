from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/login-status/', views.login_status, name='login_status'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/registrations/', views.registrations_list, name='registrations_list'),
    path('api/registrations/<int:pk>/accept/', views.registration_accept, name='registration_accept'),
    path('api/families/', views.family_list, name='family_list'),
    # Add more paths for other endpoints
]
