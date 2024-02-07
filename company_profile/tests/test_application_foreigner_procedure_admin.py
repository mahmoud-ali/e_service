from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppForeignerProcedure

class AppForeignerProcedureAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppForeignerProcedure
    change_data = {
            'procedure_type':1,
            'procedure_from':'2024-02-01',
            'procedure_to':'2024-02-15',
            'procedure_cause':'cause here',
            'appforeignerproceduredetail_set-TOTAL_FORMS':1,
            'appforeignerproceduredetail_set-INITIAL_FORMS':0,
            'appforeignerproceduredetail_set-MIN_NUM_FORMS':1,
            'appforeignerproceduredetail_set-MAX_NUM_FORMS':1000,
            'appforeignerproceduredetail_set-0-employee_name':'abc',
            'appforeignerproceduredetail_set-0-employee_address':'123',
    }

