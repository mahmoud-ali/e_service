from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppTakhali

class AppTakhaliAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppTakhali
    change_data = {
            'technical_presentation_date':'2024-02-05',
            'cause_for_takhali':'cause here',
    }

