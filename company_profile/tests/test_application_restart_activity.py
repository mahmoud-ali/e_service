from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppRestartActivity
from ..views import AppRestartActivityListView,AppRestartActivityReadonlyView

class AppRestartActivityTests(ProCompanyTests,TestCase):
    #username = "bbb"

    list_view_class = AppRestartActivityListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_restart_activity_list'
    list_url_path = '/app_restart_activity/'
    list_html_contain_ar = ['قائمة طلبات مزاولة نشاط']
    list_html_contain_en = ['List of Restart Activities']

    show_view_class = AppRestartActivityReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_restart_activity_show'
    show_url_path = '/app_restart_activity/%d/show/'
    show_html_contain_ar = ['عرض طلب مزاولة نشاط']
    show_html_contain_en = ['Show Restart Activity']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_restart_activity_add'
    add_url_path = '/app_restart_activity/add/'
    add_html_contain_ar = ['اضافة طلب مزاولة نشاط']
    add_html_contain_en = ['Add Restart Activity']

    add_model = AppRestartActivity
    add_data = {
    }
    add_file_data = ['attachement_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

