from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppMda

class AppMdaAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppMda
    change_data = {
            'mda_from':'2024-02-05',
            'mda_to':'2024-02-05',
            'cause_for_mda':'cause here',
    }

