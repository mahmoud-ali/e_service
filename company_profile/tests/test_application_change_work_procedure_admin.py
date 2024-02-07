from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppChangeWorkProcedure

class AppChangeWorkProcedureAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppChangeWorkProcedure
    change_data = {
            'reason_for_change':'reason here',
            'purpose_for_change':'purpose here',
            'rational_reason':'cause here',
    }

