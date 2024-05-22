from django.urls import path
from .views import ApplicationRecordListView, ApplicationRecordCreateView, \
                   ApplicationRecordUpdateView,ApplicationRecordReadonlyView,ApplicationRecordDeleteView, \
                   ApplicationDepartmentProcessingListView,ApplicationDepartmentProcessingUpdateView, \
                   ApplicationDepartmentProcessingReadonlyView,ApplicationExectiveProcessingListView, \
                   ApplicationExectiveProcessingUpdateView,ApplicationExectiveProcessingReadonlyView, \
                   ApplicationDeliveryListView, ApplicationDeliveryUpdateView, \
                   ApplicationDeliveryReadonlyView

app_name = "doc_workflow"
urlpatterns = [                                                        
    path('', ApplicationRecordListView.as_view(), name='home'),
    path('app_record/', ApplicationRecordListView.as_view(), name='app_record_list'),
    path('app_record/<int:pk>/edit/', ApplicationRecordUpdateView.as_view(), name='app_record_edit'),    
    path('app_record/<int:pk>/show/', ApplicationRecordReadonlyView.as_view(), name='app_record_show'),    
    path('app_record/<int:pk>/delete/', ApplicationRecordDeleteView.as_view(), name='app_record_delete'),    
    path('app_record/add/', ApplicationRecordCreateView.as_view(), name='app_record_add'),

    path('department_processing/', ApplicationDepartmentProcessingListView.as_view(), name='department_processing_list'),
    path('department_processing/<int:pk>/edit/', ApplicationDepartmentProcessingUpdateView.as_view(), name='department_processing_edit'),    
    path('department_processing/<int:pk>/show/', ApplicationDepartmentProcessingReadonlyView.as_view(), name='department_processing_show'),    

    path('executive_processing/', ApplicationExectiveProcessingListView.as_view(), name='executive_processing_list'),
    path('executive_processing/<int:pk>/edit/', ApplicationExectiveProcessingUpdateView.as_view(), name='executive_processing_edit'),    
    path('executive_processing/<int:pk>/show/', ApplicationExectiveProcessingReadonlyView.as_view(), name='executive_processing_show'),    

    path('app_delivery/', ApplicationDeliveryListView.as_view(), name='app_delivery_list'),
    path('app_delivery/<int:pk>/edit/', ApplicationDeliveryUpdateView.as_view(), name='app_delivery_edit'),    
    path('app_delivery/<int:pk>/show/', ApplicationDeliveryReadonlyView.as_view(), name='app_delivery_show'),    
]