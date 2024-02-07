from django.urls import path
from django.conf.urls.static import static

from django.conf import settings

from .views import HomePageView, \
                   AppForignerMovementListView,AppForignerMovementCreateView,AppForignerMovementReadonlyView, \
                   AppBorrowMaterialListView,AppBorrowMaterialCreateView,AppBorrowMaterialReadonlyView, \
                   LkpLocalitySelectView
                                    

app_name = "profile"
urlpatterns = [                                                        
    path('', HomePageView.as_view(), name='home'),

    path('lkp_locality/<int:master_id>/<int:dependent_id>/', LkpLocalitySelectView.as_view(), name='lkp_locality_select'),
    
    path('app_foreigner/', AppForignerMovementListView.as_view(), name='app_foreigner_list'),
    path('app_foreigner/<int:type>/', AppForignerMovementListView.as_view(), name='app_foreigner_list'),
    path('app_foreigner/<int:pk>/show/', AppForignerMovementReadonlyView.as_view(), name='app_foreigner_show'),
    path('app_foreigner/add/', AppForignerMovementCreateView.as_view(), name='app_foreigner_add'),
    
    path('app_borrow_materials/', AppBorrowMaterialListView.as_view(), name='app_borrow_list'),
    path('app_borrow_materials/<int:type>/', AppBorrowMaterialListView.as_view(), name='app_borrow_list'),
    path('app_borrow_materials/<int:pk>/show/', AppBorrowMaterialReadonlyView.as_view(), name='app_borrow_show'),    
    path('app_borrow_materials/add/', AppBorrowMaterialCreateView.as_view(), name='app_borrow_add'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
