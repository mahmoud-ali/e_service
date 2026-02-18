from django.urls import path
from form15_tra.views import (
    DashboardView, CollectionCreateView, CollectionDetailView, CollectionActionView,
    CollectionUpdateView, InvoicePrintView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='collection-list'),
    path('new/', CollectionCreateView.as_view(), name='collection-create'),
    path('<int:pk>/', CollectionDetailView.as_view(), name='collection-detail'),
    path('<int:pk>/edit/', CollectionUpdateView.as_view(), name='collection-edit'),
    path('<int:pk>/print/', InvoicePrintView.as_view(), name='invoice-print'),
    path('<int:pk>/<str:action>/', CollectionActionView.as_view(), name='collection-action'),
]
