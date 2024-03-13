from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppCyanideCertificate
from ..views import AppCyanideCertificateListView,AppCyanideCertificateReadonlyView

class AppCyanideCertificateTests(ProCompanyTests,TestCase):
    #username = "bbb"

    list_view_class = AppCyanideCertificateListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_cyanide_certificate_list'
    list_url_path = '/app_cyanide_certificate/'
    list_html_contain_ar = ['قائمة طلبات استخراج شهادة مستخدم سيانيد']
    list_html_contain_en = ['List of Cyanide Certificates']

    show_view_class = AppCyanideCertificateReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_cyanide_certificate_show'
    show_url_path = '/app_cyanide_certificate/%d/show/'
    show_html_contain_ar = ['عرض طلب شهادة مستخدم سيانيد']
    show_html_contain_en = ['Show Cyanide Certificate']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_cyanide_certificate_add'
    add_url_path = '/app_cyanide_certificate/add/'
    add_html_contain_ar = ['اضافة طلب شهادة مستخدم سيانيد']
    add_html_contain_en = ['Add Cyanide Certificate']

    add_model = AppCyanideCertificate
    add_data = {
    }
    add_file_data = ['attachement_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

