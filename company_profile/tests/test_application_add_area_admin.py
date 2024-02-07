from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppAddArea

class AppAddAreaAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppAddArea
    change_data = {
            'area_in_km2':15,
            'cause_for_addition':'cause here',
    }

