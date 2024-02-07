from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppAifaaJomrki

class AppAifaaJomrkiAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppAifaaJomrki
    change_data = {
            'license_type':2,
            'appaifaajomrkidetail_set-TOTAL_FORMS':1,
            'appaifaajomrkidetail_set-INITIAL_FORMS':0,
            'appaifaajomrkidetail_set-MIN_NUM_FORMS':1,
            'appaifaajomrkidetail_set-MAX_NUM_FORMS':1000,
            'appaifaajomrkidetail_set-0-material_name':'abc',
    }

