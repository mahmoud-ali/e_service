from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppRestartActivity

class AppRestartActivityAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppRestartActivity
    change_data = {
    }

