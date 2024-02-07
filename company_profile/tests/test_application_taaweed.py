from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppTaaweed
from ..views import AppTaaweedListView,AppTaaweedReadonlyView

class AppTaaweedTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppTaaweedListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_taaweed_list'
    list_url_path = '/app_taaweed/'
    list_html_contain_ar = ['قائمة طلبات تعويض']
    list_html_contain_en = ['List of taaweed']

    show_view_class = AppTaaweedReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_taaweed_show'
    show_url_path = '/app_taaweed/%d/show/'
    show_html_contain_ar = ['عرض طلب تعويض']
    show_html_contain_en = ['Show taaweed']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_taaweed_add'
    add_url_path = '/app_taaweed/add/'
    add_html_contain_ar = ['اضافة طلب تعويض']
    add_html_contain_en = ['Add taaweed']

    add_model = AppTaaweed
    add_data = {
            'taaweed_from':'2024-02-05',
            'taaweed_to':'2024-02-05',
            'cause_for_taaweed':'cause here',
    }
    add_file_data = []

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

