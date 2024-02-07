from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppBorrowMaterial
from ..views import AppBorrowMaterialListView,AppBorrowMaterialReadonlyView

class AppBorrowMaterialTests(ProCompanyTests,TestCase):
    language = "en"
    username = "admin"

    list_view_class = AppBorrowMaterialListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_borrow_list'
    list_url_path = '/app_borrow_materials/'
    list_html_contain = 'List of borrow materials'

    show_view_class = AppBorrowMaterialReadonlyView
    show_template_name = 'company_profile/application_readonly_master_details.html'
    show_url_name = 'profile:app_borrow_show'
    show_url_path = '/app_borrow_materials/%d/show/'
    show_html_contain = 'Show borrow materials'

    add_template_name = 'company_profile/application_add_master_details.html'
    add_url_name = 'profile:app_borrow_add'
    add_url_path = '/app_borrow_materials/add/'
    add_html_contain = 'Add new borrow materials'
    add_email_subject_contain = 'New application submitted'
    add_email_body_contain = 'Go here'
    add_model = AppBorrowMaterial
    add_data = {
            'company_from':2,
            'borrow_date':'2024-01-01',
            'appborrowmaterialdetail_set-TOTAL_FORMS':1,
            'appborrowmaterialdetail_set-INITIAL_FORMS':0,
            'appborrowmaterialdetail_set-MIN_NUM_FORMS':1,
            'appborrowmaterialdetail_set-MAX_NUM_FORMS':1000,
            'appborrowmaterialdetail_set-0-material':'Golden tool',
            'appborrowmaterialdetail_set-0-quantity':1,            
    }
    add_file_data = ['borrow_materials_list_file','borrow_from_approval_file']

