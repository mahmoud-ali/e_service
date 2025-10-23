from django.urls import path
from . import views

app_name = 'sandog'

urlpatterns = [
    path('', views.portal_home, name='portal_home'),
    path('registrations/', views.registration_list, name='registration_list'),
    path('registrations/<int:pk>/', views.registration_detail, name='registration_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('payment-methods/', views.payment_method_list, name='payment_method_list'),
]
