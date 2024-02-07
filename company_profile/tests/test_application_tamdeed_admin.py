from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppTamdeed

class AppTamdeedAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppTamdeed
    change_data = {
            'tamdeed_from':'2024-02-05',
            'tamdeed_to':'2024-02-05',
            'cause_for_tamdeed':'cause here',
    }

