from django.urls import path
from django.contrib.auth import views as auth_views
from hr_bot import portal_views, api_views

urlpatterns = [
    path('portal/', portal_views.portal_home, name='portal_home'),
    path('portal/profile/', portal_views.portal_profile, name='portal_profile'),
    path('portal/family/', portal_views.portal_family, name='portal_family'),
    path('portal/moahil/', portal_views.portal_moahil, name='portal_moahil'),
    path('portal/bank-account/', portal_views.portal_bank_account, name='portal_bank_account'),
    path('portal/logout/', portal_views.portal_logout, name='portal_logout'),
    
    path('portal/login/', auth_views.LoginView.as_view(template_name='hr_bot/portal/login.html'), name='portal_login'),
    
    path('api/employee/', api_views.get_employee_data, name='api_employee_data'),
    
    path('api/family/', api_views.get_family_list, name='api_family_list'),
    path('api/family/create/', api_views.create_family, name='api_family_create'),
    path('api/family/<int:family_id>/delete/', api_views.delete_family, name='api_family_delete'),
    
    path('api/moahil/', api_views.get_moahil_list, name='api_moahil_list'),
    path('api/moahil/create/', api_views.create_moahil, name='api_moahil_create'),
    path('api/moahil/<int:moahil_id>/delete/', api_views.delete_moahil, name='api_moahil_delete'),
    
    path('api/bank-account/', api_views.get_bank_account_list, name='api_bank_account_list'),
    path('api/bank-account/create/', api_views.create_bank_account, name='api_bank_account_create'),
    path('api/bank-account/<int:account_id>/delete/', api_views.delete_bank_account, name='api_bank_account_delete'),
]
