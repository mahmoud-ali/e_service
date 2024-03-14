from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppFuelPermission

class AppFuelPermissionAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppFuelPermission
    change_data = {
    }

