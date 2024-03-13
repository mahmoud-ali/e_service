from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppExplosivePermission

class AppExplosivePermissionAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppExplosivePermission
    change_data = {
    }

