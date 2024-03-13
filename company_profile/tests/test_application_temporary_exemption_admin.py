from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppTemporaryExemption

class AppTemporaryExemptionAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppTemporaryExemption
    change_data = {
    }

