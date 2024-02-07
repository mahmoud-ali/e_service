from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppRemoveArea

class AppRemoveAreaAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppRemoveArea
    change_data = {
            'remove_type':'first',
            'area_in_km2':15,
            'area_percent_from_total':100,
    }

