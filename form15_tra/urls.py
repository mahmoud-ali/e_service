from django.urls import path
from form15_tra.views import (
    DashboardView,
    CollectionCreateView,
    CollectionDetailView,
    CollectionStatusPollView,
    CollectionActionView,
    CollectionUpdateView,
    InvoicePrintView,
    ReceiptPrintView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='collection-list'),
    path('new/', CollectionCreateView.as_view(), name='collection-create'),
    path('<int:pk>/', CollectionDetailView.as_view(), name='collection-detail'),
    path('<int:pk>/edit/', CollectionUpdateView.as_view(), name='collection-edit'),
    path('<int:pk>/print/', InvoicePrintView.as_view(), name='invoice-print'),
    path('<int:pk>/receipt/', ReceiptPrintView.as_view(), name='receipt-print'),
    path('<int:pk>/status/', CollectionStatusPollView.as_view(), name='collection-status-poll'),
    path('<int:pk>/<str:action>/', CollectionActionView.as_view(), name='collection-action'),
]
