from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppMda
from ..views import AppMdaListView,AppMdaReadonlyView

class AppMdaTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppMdaListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_mda_list'
    list_url_path = '/app_mda/'
    list_html_contain_ar = ['قائمة طلبات MDA']
    list_html_contain_en = ['List of mda']

    show_view_class = AppMdaReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_mda_show'
    show_url_path = '/app_mda/%d/show/'
    show_html_contain_ar = ['عرض طلب MDA']
    show_html_contain_en = ['Show mda']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_mda_add'
    add_url_path = '/app_mda/add/'
    add_html_contain_ar = ['اضافة طلب MDA']
    add_html_contain_en = ['Add mda']

    add_model = AppMda
    add_data = {
            'mda_from':'2024-02-05',
            'mda_to':'2024-02-05',
            'cause_for_mda':'cause here',
    }
    add_file_data = ['approved_work_plan_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

