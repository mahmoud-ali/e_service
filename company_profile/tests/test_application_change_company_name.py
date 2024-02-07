from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppChangeCompanyName
from ..views import AppChangeCompanyNameListView,AppChangeCompanyNameReadonlyView

class AppChangeCompanyNameTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppChangeCompanyNameListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_change_company_name_list'
    list_url_path = '/app_change_company_name/'
    list_html_contain_ar = ['قائمة تغيير اسماء الشركات']
    list_html_contain_en = ['List of company name changes']

    show_view_class = AppChangeCompanyNameReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_change_company_name_show'
    show_url_path = '/app_change_company_name/%d/show/'
    show_html_contain_ar = ['عرض طلب تغيير اسم شركة']
    show_html_contain_en = ['Show company name']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_change_company_name_add'
    add_url_path = '/app_change_company_name/add/'
    add_html_contain_ar = ['اضافة اسم شركة جديد']
    add_html_contain_en = ['Add new company name']

    add_model = AppChangeCompanyName
    add_data = {
            'new_name':'technical co.ltd',
            'cause_for_change':'cause here',
    }
    add_file_data = ['tasis_certificate_file','tasis_contract_file','sh7_file','lahat_tasis_file','name_change_alert_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

