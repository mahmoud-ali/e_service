from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppWorkPlan

class AppWorkPlanAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppWorkPlan
    change_data = {
            'plan_from':'2024-02-02',
            'plan_to':'2024-02-06',
    }

