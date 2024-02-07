from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppTnazolShraka
from ..views import AppTnazolShrakaListView,AppTnazolShrakaReadonlyView

class AppTnazolShrakaTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppTnazolShrakaListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_tnazol_shraka_list'
    list_url_path = '/app_tnazol_shraka/'
    list_html_contain_ar = ['قائمة طلبات التنازل عن شركة او اسهم']
    list_html_contain_en = ['List of tnazol shraka']

    show_view_class = AppTnazolShrakaReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_tnazol_shraka_show'
    show_url_path = '/app_tnazol_shraka/%d/show/'
    show_html_contain_ar = ['عرض طلب تنازل عن شركة او سهم']
    show_html_contain_en = ['Show tnazol shraka']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_tnazol_shraka_add'
    add_url_path = '/app_tnazol_shraka/add/'
    add_html_contain_ar = ['اضافة طلب تنازل عن شركة او سهم']
    add_html_contain_en = ['Add tnazol shraka']

    add_model = AppTnazolShraka
    add_data = {
            'tnazol_type':'partial',
            'tnazol_for':'Mahmoud',
            'cause_for_tnazol':'cause here',
    }
    add_file_data = ['financial_ability_file','cv_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

