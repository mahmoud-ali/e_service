from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppExportGold
from ..views import AppExportGoldListView,AppExportGoldReadonlyView

class AppExportGoldTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppExportGoldListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_export_gold_list'
    list_url_path = '/app_export_gold/'
    list_html_contain_ar = ['قائمة طابات صادر ذهب']
    list_html_contain_en = ['List of export gold']

    show_view_class = AppExportGoldReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_export_gold_show'
    show_url_path = '/app_export_gold/%d/show/'
    show_html_contain_ar = ['عرض طلب صادر ذهب']
    show_html_contain_en = ['Show export gold']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_export_gold_add'
    add_url_path = '/app_export_gold/add/'
    add_html_contain_ar = ['اضافة طلب صادر ذهب']
    add_html_contain_en = ['Add export gold']

    add_model = AppExportGold
    add_data = {
            'total_in_gram':50,
            'net_in_gram':40,
            'zakat_in_gram':5,
            'awaad_jalila_in_gram':5,
            'arbah_amal_in_gram':5,
            'sold_for_bank_of_sudan_in_gram':4,
            'amount_to_export_in_gram':3,
            'remain_in_gram':10,
    }
    add_file_data = ['f1','f2','f3','f4','f5','f6','f7','f8','f9']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

