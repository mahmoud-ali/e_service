from django.urls import path

from django.conf import settings

from .views import Badalat,Khosomat, Mobashara


app_name = "hr"
urlpatterns = [                                                        
    path('payroll/badalat', Badalat.as_view(), name='payroll_badalat'),
    path('payroll/khosomat', Khosomat.as_view(), name='payroll_khosomat'),
    path('payroll/mobashara', Mobashara.as_view(), name='payroll_mobashara'),

]