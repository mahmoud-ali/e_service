from django.urls import path
from maintenance import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('request/new/',              views.NewRequestView.as_view(),    name='new_request'),
    path('request/<int:pk>/',         views.RequestDetailView.as_view(), name='request_detail'),
    path('request/<int:pk>/rate/',    views.RateServiceView.as_view(),   name='rate_service'),
    path('my-requests/',              views.MyRequestsView.as_view(),    name='my_requests'),

    path('technician/',               views.TechnicianRequestListView.as_view(),   name='technician_request_list'),
    path('technician/<int:pk>/',      views.TechnicianRequestDetailView.as_view(), name='technician_request_detail'),

    path('store/',                    views.StoreDashboardView.as_view(),       name='store_dashboard'),
    path('store/parts/',              views.SparePartListView.as_view(),         name='spare_part_list'),
    path('store/parts/add/',          views.SparePartCreateView.as_view(),       name='spare_part_create'),
    path('store/parts/<int:pk>/edit/', views.SparePartUpdateView.as_view(),      name='spare_part_update'),
    path('store/movements/',          views.StockMovementListView.as_view(),     name='stock_movement_list'),
    path('store/movements/add/',      views.StockMovementCreateView.as_view(),   name='stock_movement_create'),
    path('store/alerts/',             views.LowStockAlertListView.as_view(),     name='low_stock_alerts'),

    path('admin-panel/',                      views.AdminDashboardView.as_view(),        name='admin_dashboard'),
    path('admin-panel/requests/',             views.AdminAllRequestsView.as_view(),      name='admin_all_requests'),
    path('admin-panel/requests/print/',       views.AdminPrintReportView.as_view(),      name='admin_print_report'),
    path('admin-panel/requests/<int:pk>/',    views.AdminRequestDetailView.as_view(),    name='admin_request_detail'),
    path('admin-panel/requests/<int:pk>/assign/', views.AdminAssignTechnicianView.as_view(), name='admin_assign_technician'),

    path('safety/',                                   views.SafetyDashboardView.as_view(),          name='safety_dashboard'),
    path('safety/request/<int:request_pk>/permit/',   views.SafetyPermitCreateUpdateView.as_view(), name='safety_permit_form'),
    path('safety/request/<int:request_pk>/approve/',  views.SafetyPermitApproveView.as_view(),        name='safety_permit_approve'),
    path('safety/request/<int:request_pk>/close/',    views.SafetyPermitCloseView.as_view(),          name='safety_permit_close'),

    path('technical-technicians/',            views.TechnicalTechnicianListView.as_view(), name='technical_technician_list'),

    path('ajax/fault-categories/',            views.get_fault_categories,        name='ajax_fault_categories'),
    path('ajax/apartments/',                  views.get_apartments,              name='ajax_get_apartments'),
    path('ajax/technical-technicians/add/',   views.ajax_add_technical_technician, name='ajax_add_technical_technician'),
    path('ajax/notifications/',               views.notifications_list,           name='notifications_list'),
    path('ajax/notifications/<int:pk>/read/', views.mark_notification_read,      name='mark_notification_read'),
]
