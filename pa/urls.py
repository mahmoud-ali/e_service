from django.urls import path
from django.conf.urls.static import static

from django.conf import settings

from pa.views.commitment import TblCompanyCommitmentDeleteView, TblCompanyCommitmentUpdateView
from pa.views.payment import TblCompanyPaymentDeleteView, TblCompanyPaymentUpdateView
from pa.views.request import TblCompanyRequestDeleteView, TblCompanyRequestUpdateView

from .views import TblCompanyCommitmentListView,TblCompanyCommitmentCreateView,TblCompanyCommitmentReadonlyView, \
                   TblCompanyRequestListView,TblCompanyRequestCreateView,TblCompanyRequestReadonlyView, \
                   TblCompanyPaymentListView,TblCompanyPaymentCreateView,TblCompanyPaymentReadonlyView


app_name = "pa"
urlpatterns = [                                                        
    # path('', HomePageView.as_view(), name='home'),

    path('commitment/', TblCompanyCommitmentListView.as_view(), name='commitment_list'),
    path('commitment/<int:type>/', TblCompanyCommitmentListView.as_view(), name='commitment_list'),
    path('commitment/<int:pk>/edit/', TblCompanyCommitmentUpdateView.as_view(), name='commitment_edit'),    
    path('commitment/<int:pk>/show/', TblCompanyCommitmentReadonlyView.as_view(), name='commitment_show'),    
    path('commitment/<int:pk>/delete/', TblCompanyCommitmentDeleteView.as_view(), name='commitment_delete'),    
    path('commitment/add/', TblCompanyCommitmentCreateView.as_view(), name='commitment_add'),

    path('request/', TblCompanyRequestListView.as_view(), name='request_list'),
    path('request/<int:type>/', TblCompanyRequestListView.as_view(), name='request_list'),
    path('request/<int:pk>/edit/', TblCompanyRequestUpdateView.as_view(), name='request_edit'),    
    path('request/<int:pk>/show/', TblCompanyRequestReadonlyView.as_view(), name='request_show'),    
    path('request/<int:pk>/delete/', TblCompanyRequestDeleteView.as_view(), name='request_delete'),    
    path('request/add/', TblCompanyRequestCreateView.as_view(), name='request_add'),

    path('payment/', TblCompanyPaymentListView.as_view(), name='payment_list'),
    path('payment/<int:type>/', TblCompanyPaymentListView.as_view(), name='payment_list'),
    path('payment/<int:pk>/edit/', TblCompanyPaymentUpdateView.as_view(), name='payment_edit'),    
    path('payment/<int:pk>/show/', TblCompanyPaymentReadonlyView.as_view(), name='payment_show'),    
    path('payment/<int:pk>/delete/', TblCompanyPaymentDeleteView.as_view(), name='payment_delete'),    
    path('payment/add/', TblCompanyPaymentCreateView.as_view(), name='payment_add'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
