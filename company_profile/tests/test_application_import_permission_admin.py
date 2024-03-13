from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppImportPermission

class AppImportPermissionAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppImportPermission
    change_data = {
    }

