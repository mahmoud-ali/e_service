from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppRenewalContract

class AppRenewalContractAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppRenewalContract
    change_data = {
    }

