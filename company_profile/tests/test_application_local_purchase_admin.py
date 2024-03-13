from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppLocalPurchase

class AppLocalPurchaseAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppLocalPurchase
    change_data = {
    }

