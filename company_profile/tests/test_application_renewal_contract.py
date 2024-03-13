from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppRenewalContract
from ..views import AppRenewalContractListView,AppRenewalContractReadonlyView

class AppRenewalContractTests(ProCompanyTests,TestCase):
    #username = "bbb"

    list_view_class = AppRenewalContractListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_renewal_contract_list'
    list_url_path = '/app_renewal_contract/'
    list_html_contain_ar = ['قائمة طلبات تجديد عقود مخلفات تعدين']
    list_html_contain_en = ['List of Renewal Contracts']

    show_view_class = AppRenewalContractReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_renewal_contract_show'
    show_url_path = '/app_renewal_contract/%d/show/'
    show_html_contain_ar = ['عرض طلب تجديد عقد مخلفات تعدين']
    show_html_contain_en = ['Show Renewal Contract']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_renewal_contract_add'
    add_url_path = '/app_renewal_contract/add/'
    add_html_contain_ar = ['اضافة طلب تجديد عقد مخلفات تعدين']
    add_html_contain_en = ['Add Renewal Contract']

    add_model = AppRenewalContract
    add_data = {
    }
    add_file_data = ['attachement_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

