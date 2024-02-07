from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppTechnicalFinancialReport

class AppTechnicalFinancialReportAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppTechnicalFinancialReport
    change_data = {
            'report_from':'2024-02-02',
            'report_to':'2024-02-06',
            'report_type':'technical',
            'report_comments':'comments here',
    }

