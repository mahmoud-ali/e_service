from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppLocalPurchase
from ..views import AppLocalPurchaseListView,AppLocalPurchaseReadonlyView

class AppLocalPurchaseTests(ProCompanyTests,TestCase):
    #username = "bbb"

    list_view_class = AppLocalPurchaseListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_local_purchase_list'
    list_url_path = '/app_local_purchase/'
    list_html_contain_ar = ['قائمة طلبات شراء محلي']
    list_html_contain_en = ['List of Local Purchases']

    show_view_class = AppLocalPurchaseReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_local_purchase_show'
    show_url_path = '/app_local_purchase/%d/show/'
    show_html_contain_ar = ['عرض طلب شراء محلي']
    show_html_contain_en = ['Show Local Purchase']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_local_purchase_add'
    add_url_path = '/app_local_purchase/add/'
    add_html_contain_ar = ['اضافة طلب شراء محلي']
    add_html_contain_en = ['Add Local Purchase']

    add_model = AppLocalPurchase
    add_data = {
    }
    add_file_data = ['attachement_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

