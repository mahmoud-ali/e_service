from django.urls import path
from . import views

urlpatterns = [
    path('', views.needs_request_list, name='needs_request_list'),
    path('new/', views.needs_request_create, name='needs_request_create'),
    path('<int:pk>/', views.needs_request_detail, name='needs_request_detail'),
    path('<int:pk>/update/', views.needs_request_update, name='needs_request_update'),
]
