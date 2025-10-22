from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/login-status/', views.login_status, name='login_status'),
    path('api/logout/', views.api_logout, name='api_logout'),
    
    path('api/registrations/<int:state>/', views.registrations_list, name='registrations_list'),
    path('api/registrations/<int:pk>/accept/', views.registration_accept, name='registration_accept'),
    path('api/registrations/<int:pk>/reject/', views.registration_reject, name='registration_reject'),
    path('api/registrations/<int:pk>/reset-password/', views.registration_reset_password, name='registration_reset_password'),
    
    path('api/families/', views.family_list, name='family_list'),
    path('api/families/create/', views.family_create, name='family_create'),
    path('api/families/<int:pk>/accept/', views.family_accept, name='family_accept'),
    path('api/families/<int:pk>/reject/', views.family_reject, name='family_reject'),
    
    path('api/moahil/', views.moahil_list, name='moahil_list'),
    path('api/moahil/create/', views.moahil_create, name='moahil_create'),
    path('api/moahil/<int:pk>/accept/', views.moahil_accept, name='moahil_accept'),
    path('api/moahil/<int:pk>/reject/', views.moahil_reject, name='moahil_reject'),
    
    path('api/bank-accounts/', views.bank_account_list, name='bank_account_list'),
    path('api/bank-accounts/create/', views.bank_account_create, name='bank_account_create'),
    path('api/bank-accounts/<int:pk>/accept/', views.bank_account_accept, name='bank_account_accept'),
    path('api/bank-accounts/<int:pk>/reject/', views.bank_account_reject, name='bank_account_reject'),
    
    path('api/employee-data/', views.employee_data, name='employee_data'),
]
