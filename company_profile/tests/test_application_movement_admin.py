from django.test import TestCase
from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppForignerMovement

class AppMovementAdminTests(ProCompanyAdminTests,TestCase):
    language = "en"
    username = "admin"

    add_email_subject_contain = 'New application submitted'
    add_email_body_contain = 'Go here'
    add_model = AppForignerMovement
    add_data = {
            'route_from':'AAAAAAAAAA',
            'route_to':'BBBBBBBBBB',
            'period_from':'2024-01-01',
            'period_to':'2024-01-31',
            'address_in_sudan':'Khratoum',
            'nationality':1,
            'passport_no':'4566654',
            'passport_expiry_date':'2024-12-01',
    }
    add_file_data = ['official_letter_file','passport_copy_file','cv_file','experiance_certificates_file']

