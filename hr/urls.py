from django.urls import path

from django.conf import settings

from .views import Badalat, CheckPayroll, FargKhosomat,Khosomat, KhosomatPlusMokaf2, M2moria, MajlisEl2daraMokaf2View, Mobashara, Modir3amBadalatView, Modir3amKhosomatView, Modir3amMokaf2View, Mokaf2,FargBadalat, Ta3agodMosimiMokaf2, Ta3agodMosimiMoratab, Tasoia, Wi7datMosa3idaMokaf2tFarigMoratab,Wi7datMosa3idaMokaf2t

app_name = "hr"
urlpatterns = [                                                        
    path('payroll/badalat', Badalat.as_view(), name='payroll_badalat'),
    path('payroll/khosomat', Khosomat.as_view(), name='payroll_khosomat'),
    path('payroll/check_payroll', CheckPayroll.as_view(), name='payroll_check'),
    path('payroll/mobashara', Mobashara.as_view(), name='payroll_mobashara'),
    path('payroll/mokaf2', Mokaf2.as_view(), name='payroll_mokaf2'),
    path('payroll/moratab_mokaf2', KhosomatPlusMokaf2.as_view(), name='payroll_moratab_mokaf2'),
    path('payroll/m2moria', M2moria.as_view(), name='payroll_m2moria'),

    path('payroll/diff_badalat', FargBadalat.as_view(), name='payroll_diff_badalat'),
    path('payroll/diff_khosomat', FargKhosomat.as_view(), name='payroll_diff_khosomat'),

    path('payroll/wi7dat_mosa3ida_farg_moratab', Wi7datMosa3idaMokaf2tFarigMoratab.as_view(), name='payroll_wi7dat_mosa3ida_farg_moratab'),
    path('payroll/wi7dat_mosa3ida_mokaf2', Wi7datMosa3idaMokaf2t.as_view(), name='payroll_wi7dat_mosa3ida_mokaf2'),

    path('payroll/ta3agod_mosimi_moratab', Ta3agodMosimiMoratab.as_view(), name='payroll_ta3agod_mosimi_moratab'),
    path('payroll/ta3agod_mosimi_mokaf2', Ta3agodMosimiMokaf2.as_view(), name='payroll_ta3agod_mosimi_mokaf2'),

    path('payroll/majlis_el2dara_mokaf2', MajlisEl2daraMokaf2View.as_view(), name='payroll_majlis_el2dara_mokaf2'),

    path('payroll/modir_3am_badalat', Modir3amBadalatView.as_view(), name='payroll_modir_3am_badalat'),
    path('payroll/modir_3am_khosomat', Modir3amKhosomatView.as_view(), name='payroll_modir_3am_khosomat'),
    path('payroll/modir_3am_mokaf2', Modir3amMokaf2View.as_view(), name='payroll_modir_3am_mokaf2'),
    path('payroll/tasoia', Tasoia.as_view(), name='payroll_tasoia'),

]