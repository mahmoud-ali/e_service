from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppForignerMovement
from ..views import AppForignerMovementListView,AppForignerMovementReadonlyView

class AppMovementTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppForignerMovementListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_foreigner_list'
    list_url_path = '/app_foreigner/'
    list_html_contain_ar = ['قائمة طلبات حركة الاجانب']
    list_html_contain_en = ['List of foreigner movements']

    show_view_class = AppForignerMovementListView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_foreigner_show'
    show_url_path = '/app_foreigner/%d/show/'
    show_html_contain_ar = ['عرض طلب حركة اجنبي']
    show_html_contain_en = ['Show movement']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_foreigner_add'
    add_url_path = '/app_foreigner/add/'
    add_html_contain_ar = ['طلب تحرك اجنبي']
    add_html_contain_en = ['Add new movement']

    add_model = AppForignerMovement
    add_data = {
            'route_from':'AAAAAAAAAA',
            'route_to':'BBBBBBBBBB',
            'period_from':'2024-01-01',
            'period_to':'2024-01-31',
            'address_in_sudan':'Khratoum',
            'nationality':1,
            'passport_no':'4566654',
            'passport_expiry_date':'2024-12-01',
    }
    add_file_data = ['official_letter_file','passport_copy_file','cv_file','experiance_certificates_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

