from django.urls import path
from django.conf.urls.static import static

from django.conf import settings

from .views import TblCompanyCommitmentListView,TblCompanyCommitmentCreateView,TblCompanyCommitmentReadonlyView

app_name = "pa"
urlpatterns = [                                                        
    # path('', HomePageView.as_view(), name='home'),

    path('commitment/', TblCompanyCommitmentListView.as_view(), name='commitment_list'),
    path('commitment/<int:type>/', TblCompanyCommitmentListView.as_view(), name='commitment_list'),
    path('commitment/<int:pk>/show/', TblCompanyCommitmentReadonlyView.as_view(), name='commitment_show'),    
    path('commitment/add/', TblCompanyCommitmentCreateView.as_view(), name='commitment_add'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
