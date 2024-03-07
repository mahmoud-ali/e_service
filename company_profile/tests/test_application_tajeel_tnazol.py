from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppTajeelTnazol
from ..views import AppTajeelTnazolListView,AppTajeelTnazolReadonlyView

class AppTajeelTnazolTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppTajeelTnazolListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_tajeel_tnazol_list'
    list_url_path = '/app_tajeel_tnazol/'
    list_html_contain_ar = ['قائمة طلبات تأجيل تنازل']
    list_html_contain_en = ['List of postponed assignment']

    show_view_class = AppTajeelTnazolReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_tajeel_tnazol_show'
    show_url_path = '/app_tajeel_tnazol/%d/show/'
    show_html_contain_ar = ['عرض طلب تأجيل تنازل']
    show_html_contain_en = ['Show postponed assignment']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_tajeel_tnazol_add'
    add_url_path = '/app_tajeel_tnazol/add/'
    add_html_contain_ar = ['اضافة طلب تأجيل تنازل']
    add_html_contain_en = ['Add postponed assignment']

    add_model = AppTajeelTnazol
    add_data = {
            'tnazol_type':'first',
            'cause_for_tajeel':'cause here',
    }
    add_file_data = ['cause_for_tajeel_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

