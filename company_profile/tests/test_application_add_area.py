from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppAddArea
from ..views import AppAddAreaListView,AppAddAreaReadonlyView

class AppAddAreaTests(ProCompanyTests,TestCase):
    #username = "bbb"

    list_view_class = AppAddAreaListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_add_area_list'
    list_url_path = '/app_add_area/'
    list_html_contain_ar = ['قائمة طلبات اضافة مساحة']
    list_html_contain_en = ['List of Added area']

    show_view_class = AppAddAreaReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_add_area_show'
    show_url_path = '/app_add_area/%d/show/'
    show_html_contain_ar = ['عرض طلب المساحة المضافة']
    show_html_contain_en = ['Show added area']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_add_area_add'
    add_url_path = '/app_add_area/add/'
    add_html_contain_ar = ['اضافة مساحة جديدة']
    add_html_contain_en = ['Add new area']

    add_model = AppAddArea
    add_data = {
            'area_in_km2':15,
            'cause_for_addition':'cause here',
    }
    add_file_data = ['geo_coordination_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

