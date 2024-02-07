from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppExplorationTime
from ..views import AppExplorationTimeListView,AppExplorationTimeReadonlyView

class AppExplorationTimeTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppExplorationTimeListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_exploration_time_list'
    list_url_path = '/app_exploration_time/'
    list_html_contain_ar = ['قائمة طلبات مواقيت الاستكشاف']
    list_html_contain_en = ['List of exploration times']

    show_view_class = AppExplorationTimeReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_exploration_time_show'
    show_url_path = '/app_exploration_time/%d/show/'
    show_html_contain_ar = ['عرض طلب مدة استكشاف']
    show_html_contain_en = ['Show exploration time']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_exploration_time_add'
    add_url_path = '/app_exploration_time/add/'
    add_html_contain_ar = ['اضافة طلب ميقات استكشاف']
    add_html_contain_en = ['Add new exploration time']

    add_model = AppExplorationTime
    add_data = {
            'expo_from':'2024-02-01',
            'expo_to':'2024-02-28',
            'expo_cause_for_timing':'cause here',
    }
    add_file_data = ['expo_cause_for_change_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

