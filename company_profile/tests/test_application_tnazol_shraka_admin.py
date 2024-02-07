from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppTnazolShraka

class AppTnazolShrakaAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppTnazolShraka
    change_data = {
            'tnazol_type':'partial',
            'tnazol_for':'Mahmoud',
            'cause_for_tnazol':'cause here',
    }

