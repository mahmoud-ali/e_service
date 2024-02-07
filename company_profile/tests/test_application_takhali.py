from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppTakhali
from ..views import AppTakhaliListView,AppTakhaliReadonlyView

class AppTakhaliTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppTakhaliListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_takhali_list'
    list_url_path = '/app_takhali/'
    list_html_contain_ar = ['قائمة طلبات التخلي']
    list_html_contain_en = ['List of takhali']

    show_view_class = AppTakhaliReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_takhali_show'
    show_url_path = '/app_takhali/%d/show/'
    show_html_contain_ar = ['عرض طلب تخلي']
    show_html_contain_en = ['Show takhali']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_takhali_add'
    add_url_path = '/app_takhali/add/'
    add_html_contain_ar = ['اضافة طلب تخلي']
    add_html_contain_en = ['Add takhali']

    add_model = AppTakhali
    add_data = {
            'technical_presentation_date':'2024-02-05',
            'cause_for_takhali':'cause here',
    }
    add_file_data = ['technical_report_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

