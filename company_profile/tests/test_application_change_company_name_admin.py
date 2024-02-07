from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppChangeCompanyName

class AppChangeCompanyNameAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppChangeCompanyName
    change_data = {
            'new_name':'technical co.ltd',
            'cause_for_change':'cause here',
    }

