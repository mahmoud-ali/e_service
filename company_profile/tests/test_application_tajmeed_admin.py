from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppTajmeed

class AppTajmeedAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppTajmeed
    change_data = {
            'tajmeed_from':'2024-02-05',
            'tajmeed_to':'2024-02-15',
            'cause_for_tajmeed':'cause here',
    }

