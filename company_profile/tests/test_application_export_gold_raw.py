from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppExportGoldRaw
from ..views import AppExportGoldRawListView,AppExportGoldRawReadonlyView

class AppExportGoldRawTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppExportGoldRawListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_export_gold_raw_list'
    list_url_path = '/app_export_gold_raw/'
    list_html_contain_ar = ['قائمة طلبات صادر خام']
    list_html_contain_en = ['List of exported raw material']

    show_view_class = AppExportGoldRawReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_export_gold_raw_show'
    show_url_path = '/app_export_gold_raw/%d/show/'
    show_html_contain_ar = ['عرض طلب صادر خام']
    show_html_contain_en = ['Show exported raw material']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_export_gold_raw_add'
    add_url_path = '/app_export_gold_raw/add/'
    add_html_contain_ar = ['اضافة طلب صادر خام']
    add_html_contain_en = ['Add exported raw material']

    add_model = AppExportGoldRaw
    add_data = {
            'mineral':1,
            'license_type':'license1',
            'amount_in_gram':5,
            'sale_price':5,
            'export_country':'Egypt',
            'export_city':'Cairo',
            'export_address':'street 12',
    }
    add_file_data = ['f11','f12','f13','f14','f15','f16','f17','f18','f19']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

