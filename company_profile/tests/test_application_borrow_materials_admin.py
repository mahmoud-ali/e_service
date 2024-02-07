from django.test import TestCase
from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppBorrowMaterial

class AppBorrowMaterialAdminTests(ProCompanyAdminTests,TestCase):
    language = "en"
    username = "admin"

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

