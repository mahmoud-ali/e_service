from django.urls import path

from django.conf import settings

from .views import Badalat, FargKhosomat,Khosomat, M2moria, Mobashara, Mokaf2,FargBadalat


app_name = "hr"
urlpatterns = [                                                        
    path('payroll/badalat', Badalat.as_view(), name='payroll_badalat'),
    path('payroll/khosomat', Khosomat.as_view(), name='payroll_khosomat'),
    path('payroll/mobashara', Mobashara.as_view(), name='payroll_mobashara'),
    path('payroll/mokaf2', Mokaf2.as_view(), name='payroll_mokaf2'),
    path('payroll/m2moria', M2moria.as_view(), name='payroll_m2moria'),

    path('payroll/diff_badalat', FargBadalat.as_view(), name='payroll_diff_badalat'),
    path('payroll/diff_khosomat', FargKhosomat.as_view(), name='payroll_diff_khosomat'),

]