from django.urls import path
from django.conf.urls.static import static

from django.conf import settings

from pa.views.commitment import TblCompanyCommitmentConfirmStateView
from pa.views.payment import TblCompanyPaymentConfirmStateView
from pa.views.request import TblCompanyRequestConfirmStateView

from .views import TblCompanyCommitmentListView,TblCompanyCommitmentCreateView,TblCompanyCommitmentReadonlyView, \
                   TblCompanyRequestListView,TblCompanyRequestCreateView,TblCompanyRequestReadonlyView, \
                   TblCompanyPaymentListView,TblCompanyPaymentCreateView,TblCompanyPaymentReadonlyView


app_name = "pa"
urlpatterns = [                                                        
    # path('', HomePageView.as_view(), name='home'),

    path('commitment/', TblCompanyCommitmentListView.as_view(), name='commitment_list'),
    path('commitment/<int:type>/', TblCompanyCommitmentListView.as_view(), name='commitment_list'),
    path('commitment/<int:pk>/show/', TblCompanyCommitmentReadonlyView.as_view(), name='commitment_show'),    
    path('commitment/<int:pk>/confirm/', TblCompanyCommitmentConfirmStateView.as_view(), name='commitment_confirm'),    
    path('commitment/add/', TblCompanyCommitmentCreateView.as_view(), name='commitment_add'),

    path('request/', TblCompanyRequestListView.as_view(), name='request_list'),
    path('request/<int:type>/', TblCompanyRequestListView.as_view(), name='request_list'),
    path('request/<int:pk>/show/', TblCompanyRequestReadonlyView.as_view(), name='request_show'),    
    path('request/<int:pk>/confirm/', TblCompanyRequestConfirmStateView.as_view(), name='request_confirm'),    
    path('request/add/', TblCompanyRequestCreateView.as_view(), name='request_add'),

    path('payment/', TblCompanyPaymentListView.as_view(), name='payment_list'),
    path('payment/<int:type>/', TblCompanyPaymentListView.as_view(), name='payment_list'),
    path('payment/<int:pk>/show/', TblCompanyPaymentReadonlyView.as_view(), name='payment_show'),    
    path('payment/<int:pk>/confirm/', TblCompanyPaymentConfirmStateView.as_view(), name='payment_confirm'),    
    path('payment/add/', TblCompanyPaymentCreateView.as_view(), name='payment_add'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
