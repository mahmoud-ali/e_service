from django.urls import path
from . import views

app_name = 'sandog'

urlpatterns = [
    path('portal/', views.portal_home, name='portal_home'),
    path('portal/registrations/', views.registration_list, name='registration_list'),
    path('portal/registrations/<int:pk>/', views.registration_detail, name='registration_detail'),
    path('portal/categories/', views.category_list, name='category_list'),
    path('portal/payment-methods/', views.payment_method_list, name='payment_method_list'),
]
