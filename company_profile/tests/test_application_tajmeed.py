from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppTajmeed
from ..views import AppTajmeedListView,AppTajmeedReadonlyView

class AppTajmeedTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppTajmeedListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_tajmeed_list'
    list_url_path = '/app_tajmeed/'
    list_html_contain_ar = ['قائمة طلبات التجمييد']
    list_html_contain_en = ['List of tajmeed']

    show_view_class = AppTajmeedReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_tajmeed_show'
    show_url_path = '/app_tajmeed/%d/show/'
    show_html_contain_ar = ['عرض طلب تجمييد']
    show_html_contain_en = ['Show tajmeed']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_tajmeed_add'
    add_url_path = '/app_tajmeed/add/'
    add_html_contain_ar = ['اضافة طلب تجمييد']
    add_html_contain_en = ['Add tajmeed']

    add_model = AppTajmeed
    add_data = {
            'tajmeed_from':'2024-02-05',
            'tajmeed_to':'2024-02-15',
            'cause_for_tajmeed':'cause here',
    }
    add_file_data = ['cause_for_uncontrolled_force_file','letter_from_jeha_amnia_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

