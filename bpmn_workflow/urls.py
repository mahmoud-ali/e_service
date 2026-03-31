from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    WorkflowViewSet,
    ProcessInstanceViewSet,
    TaskViewSet
)
from .portal_api import (
    DashboardSummaryView,
    EmployeePortalViewSet,
    TaskInboxViewSet,
    ProcessTimelineView,
    CommentViewSet
)
from .views import EmployeePortalHomeView

router = DefaultRouter()
router.register(r'my-requests', EmployeePortalViewSet, basename='my-requests')
router.register(r'task-inbox', TaskInboxViewSet, basename='task-inbox')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'process-instances', ProcessInstanceViewSet, basename='process-instance')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('api/timeline/<uuid:pk>/', ProcessTimelineView.as_view(), name='process-timeline'),
    
    # Standard (Non-API) Views
    path('portal/', EmployeePortalHomeView.as_view(), name='portal-home'),
]
