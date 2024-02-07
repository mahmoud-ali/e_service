from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppExplorationTime

class AppExplorationTimeAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppExplorationTime
    change_data = {
            'expo_from':'2024-02-01',
            'expo_to':'2024-02-28',
            'expo_cause_for_timing':'cause here',
    }

