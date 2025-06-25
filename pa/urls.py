from django.urls import path
from django.conf.urls.static import static

from django.conf import settings

from pa.views.commitment import TblCompanyCommitmentDeleteView, TblCompanyCommitmentUpdateView
from pa.views.commitment_schedular import TblCompanyCommitmentScheduleCreateView, TblCompanyCommitmentScheduleDeleteView, TblCompanyCommitmentScheduleListView, TblCompanyCommitmentScheduleReadonlyView, TblCompanyCommitmentScheduleUpdateView
from pa.views.daily import PaDailyView
from pa.views.payment import TblCompanyPaymentDeleteView, TblCompanyPaymentUpdateView
from pa.views.payment_status import PaymentStatusView
from pa.views.request import TblCompanyRequestDeleteView, TblCompanyRequestUpdateView
from pa.views.request_status import RequestStatusView

from .views import LkpLicenseSelectView, TblCompanyOpenningBalanceListView,TblCompanyOpenningBalanceCreateView,TblCompanyOpenningBalanceReadonlyView,TblCompanyOpenningBalanceUpdateView,TblCompanyOpenningBalanceDeleteView, \
                   TblCompanyCommitmentListView,TblCompanyCommitmentCreateView,TblCompanyCommitmentReadonlyView, \
                   TblCompanyRequestListView,TblCompanyRequestCreateView,TblCompanyRequestReadonlyView, \
                   TblCompanyPaymentListView,TblCompanyPaymentCreateView,TblCompanyPaymentReadonlyView


app_name = "pa"
urlpatterns = [                                                        
    path('', PaymentStatusView.as_view(), name='home'),

    path('lkp_license/<int:master_id>/<int:dependent_id>/', LkpLicenseSelectView.as_view(), name='lkp_license_select'),

    path('openning_balance/', TblCompanyOpenningBalanceListView.as_view(), name='openning_balance_list'),
    path('openning_balance/<int:type>/', TblCompanyOpenningBalanceListView.as_view(), name='openning_balance_list'),
    path('openning_balance/<int:pk>/edit/', TblCompanyOpenningBalanceUpdateView.as_view(), name='openning_balance_edit'),    
    path('openning_balance/<int:pk>/show/', TblCompanyOpenningBalanceReadonlyView.as_view(), name='openning_balance_show'),    
    path('openning_balance/<int:pk>/delete/', TblCompanyOpenningBalanceDeleteView.as_view(), name='openning_balance_delete'),    
    path('openning_balance/add/', TblCompanyOpenningBalanceCreateView.as_view(), name='openning_balance_add'),

    path('commitment/', TblCompanyCommitmentListView.as_view(), name='commitment_list'),
    path('commitment/<int:type>/', TblCompanyCommitmentListView.as_view(), name='commitment_list'),
    path('commitment/<int:pk>/edit/', TblCompanyCommitmentUpdateView.as_view(), name='commitment_edit'),    
    path('commitment/<int:pk>/show/', TblCompanyCommitmentReadonlyView.as_view(), name='commitment_show'),    
    path('commitment/<int:pk>/delete/', TblCompanyCommitmentDeleteView.as_view(), name='commitment_delete'),    
    path('commitment/add/', TblCompanyCommitmentCreateView.as_view(), name='commitment_add'),

    path('commitment_schedule/', TblCompanyCommitmentScheduleListView.as_view(), name='commitment_schedule_list'),
    path('commitment_schedule/<int:type>/', TblCompanyCommitmentScheduleListView.as_view(), name='commitment_schedule_list'),
    path('commitment_schedule/<int:pk>/edit/', TblCompanyCommitmentScheduleUpdateView.as_view(), name='commitment_schedule_edit'),    
    path('commitment_schedule/<int:pk>/show/', TblCompanyCommitmentScheduleReadonlyView.as_view(), name='commitment_schedule_show'),    
    path('commitment_schedule/<int:pk>/delete/', TblCompanyCommitmentScheduleDeleteView.as_view(), name='commitment_schedule_delete'),    
    path('commitment_schedule/add/', TblCompanyCommitmentScheduleCreateView.as_view(), name='commitment_schedule_add'),

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

    path('daily/', PaDailyView.as_view(), name='daily_list'),
    path('request_status/', RequestStatusView.as_view(), name='request_status'),
    path('payment_status/', PaymentStatusView.as_view(), name='payment_status'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
