from django.urls import path
from . import views
from . import migrate_views
from . import fuel_views

app_name = 'fleet'

urlpatterns = [
    path('', views.portal_home, name='portal_home'),
    path('migrate/', migrate_views.migrate_page, name='migrate_page'),
    path('migrate/stats/', migrate_views.migrate_stats, name='migrate_stats'),
    path('migrate/stream/', migrate_views.migrate_stream, name='migrate_stream'),

    # Vehicles, Drivers, Missions, Maintenance Routes
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/<int:pk>/', views.driver_detail, name='driver_detail'),
    path('missions/', views.mission_list, name='mission_list'),
    path('missions/<int:pk>/', views.mission_detail, name='mission_detail'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/<int:pk>/', views.maintenance_detail, name='maintenance_detail'),

    # Fuel Management Routes
    path('fuel/', fuel_views.fuel_statement_list, name='fuel_statement_list'),
    path('fuel/<int:statement_id>/', fuel_views.fuel_statement_detail, name='fuel_statement_detail'),
    path('fuel/<int:statement_id>/generate/', fuel_views.generate_fuel_statement_items, name='generate_fuel_statement_items'),
    path('fuel/<int:statement_id>/item/save/', fuel_views.fuel_item_save, name='fuel_item_save'),
    path('fuel/<int:statement_id>/item/<int:item_id>/delete/', fuel_views.fuel_item_delete, name='fuel_item_delete'),
    path('fuel/<int:statement_id>/import/', fuel_views.import_fuel_excel, name='import_fuel_excel'),
    path('fuel/<int:statement_id>/export/', fuel_views.export_fuel_excel, name='export_fuel_excel'),
    path('fuel/api/hr-employees/', fuel_views.api_hr_employees, name='api_hr_employees'),
]


