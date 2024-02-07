from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppTaaweed

class AppTaaweedAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppTaaweed
    change_data = {
            'taaweed_from':'2024-02-05',
            'taaweed_to':'2024-02-05',
            'cause_for_taaweed':'cause here',
    }

