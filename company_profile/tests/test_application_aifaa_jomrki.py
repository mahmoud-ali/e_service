from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppAifaaJomrki
from ..views import AppAifaaJomrkiListView,AppAifaaJomrkiReadonlyView

class AppAifaaJomrkiTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppAifaaJomrkiListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_aifaa_jomrki_list'
    list_url_path = '/app_aifaa_jomrki/'
    list_html_contain_ar = ['قائمة طلبات اعفاء جمركي']
    list_html_contain_en = ['List of Aifaa Jomrki']

    show_view_class = AppAifaaJomrkiReadonlyView
    show_template_name = 'company_profile/application_readonly_master_details.html'
    show_url_name = 'profile:app_aifaa_jomrki_show'
    show_url_path = '/app_aifaa_jomrki/%d/show/'
    show_html_contain_ar = ['عرض اعفاء جمركي']
    show_html_contain_en = ['Show Aifaa Jomrki']

    add_template_name = 'company_profile/application_add_master_details.html'
    add_url_name = 'profile:app_aifaa_jomrki_add'
    add_url_path = '/app_aifaa_jomrki/add/'
    add_html_contain_ar = ['اضافة اعفاء جمركي']
    add_html_contain_en = ['Add Aifaa Jomrki']

    add_model = AppAifaaJomrki
    add_data = {
            'license_type':2,
            'appaifaajomrkidetail_set-TOTAL_FORMS':1,
            'appaifaajomrkidetail_set-INITIAL_FORMS':0,
            'appaifaajomrkidetail_set-MIN_NUM_FORMS':1,
            'appaifaajomrkidetail_set-MAX_NUM_FORMS':1000,
            'appaifaajomrkidetail_set-0-material_name':'abc',
    }
    add_file_data = ['approved_requirements_list_file','approval_from_finance_ministry_file','final_voucher_file', 'shipping_policy_file','check_certificate_file','origin_certificate_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

