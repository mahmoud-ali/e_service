from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppImportPermission

class AppImportPermissionAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppImportPermission
    change_data = {
            'appimportpermissiondetail_set-TOTAL_FORMS':1,
            'appimportpermissiondetail_set-INITIAL_FORMS':0,
            'appimportpermissiondetail_set-MIN_NUM_FORMS':1,
            'appimportpermissiondetail_set-MAX_NUM_FORMS':1000,
            'appimportpermissiondetail_set-0-import_material_name':'aaa',
            'appimportpermissiondetail_set-0-import_qty':32,
    }

