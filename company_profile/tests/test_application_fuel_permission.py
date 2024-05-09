from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppFuelPermission
from ..views import AppFuelPermissionListView,AppFuelPermissionReadonlyView

class AppFuelPermissionTests(ProCompanyTests,TestCase):
    #username = "bbb"

    list_view_class = AppFuelPermissionListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_fuel_permission_list'
    list_url_path = '/app_fuel_permission/'
    list_html_contain_ar = ['قائمة طلبات موافقة وقود']
    list_html_contain_en = ['List of Fuel Permissions']

    show_view_class = AppFuelPermissionReadonlyView
    show_template_name = 'company_profile/application_readonly_master_details.html'
    show_url_name = 'profile:app_fuel_permission_show'
    show_url_path = '/app_fuel_permission/%d/show/'
    show_html_contain_ar = ['عرض موافقة وقود']
    show_html_contain_en = ['Show Fuel Permission']

    add_template_name = 'company_profile/application_add_master_details.html'
    add_url_name = 'profile:app_fuel_permission_add'
    add_url_path = '/app_fuel_permission/add/'
    add_html_contain_ar = ['اضافة طلب موافقة وقود']
    add_html_contain_en = ['Add Fuel Permission']

    add_model = AppFuelPermission
    add_data = {
            'appfuelpermissiondetail_set-TOTAL_FORMS':1,
            'appfuelpermissiondetail_set-INITIAL_FORMS':0,
            'appfuelpermissiondetail_set-MIN_NUM_FORMS':1,
            'appfuelpermissiondetail_set-MAX_NUM_FORMS':1000,
            'appfuelpermissiondetail_set-0-fuel_type_name':'aaa',
            'appfuelpermissiondetail_set-0-fuel_qty':32,
    }
    add_file_data = ['attachement_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

