from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppLocalPurchase

class AppLocalPurchaseAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppLocalPurchase
    change_data = {
            'applocalpurchasedetail_set-TOTAL_FORMS':1,
            'applocalpurchasedetail_set-INITIAL_FORMS':0,
            'applocalpurchasedetail_set-MIN_NUM_FORMS':1,
            'applocalpurchasedetail_set-MAX_NUM_FORMS':1000,
            'applocalpurchasedetail_set-0-import_material_name':'aaa',
            'applocalpurchasedetail_set-0-import_qty':32,
    }

