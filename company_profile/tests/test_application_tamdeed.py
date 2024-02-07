from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppTamdeed
from ..views import AppTamdeedListView,AppTamdeedReadonlyView

class AppTamdeedTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppTamdeedListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_tamdeed_list'
    list_url_path = '/app_tamdeed/'
    list_html_contain_ar = ['قائمة طلبات التمديد']
    list_html_contain_en = ['List of tamdeed']

    show_view_class = AppTamdeedReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_tamdeed_show'
    show_url_path = '/app_tamdeed/%d/show/'
    show_html_contain_ar = ['عرض طلب تمديد']
    show_html_contain_en = ['Show tamdeed']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_tamdeed_add'
    add_url_path = '/app_tamdeed/add/'
    add_html_contain_ar = ['اضافة طلب تمديد']
    add_html_contain_en = ['Add tamdeed']

    add_model = AppTamdeed
    add_data = {
            'tamdeed_from':'2024-02-05',
            'tamdeed_to':'2024-02-05',
            'cause_for_tamdeed':'cause here',
    }
    add_file_data = ['approved_work_plan_file','tnazol_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

