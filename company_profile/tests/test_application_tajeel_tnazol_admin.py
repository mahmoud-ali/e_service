from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppTajeelTnazol

class AppTajeelTnazolAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppTajeelTnazol
    change_data = {
            'tnazol_type':'first',
            'cause_for_tajeel':'cause here',
    }

