from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppSendSamplesForAnalysis

class AppSendSamplesForAnalysisAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppSendSamplesForAnalysis
    change_data = {
            'lab_country':'Egypt',
            'lab_city':'Cairo',
            'lab_address':'address here',
            'lab_analysis_cost':500,
            'appsendsamplesforanalysisdetail_set-TOTAL_FORMS':1,
            'appsendsamplesforanalysisdetail_set-INITIAL_FORMS':0,
            'appsendsamplesforanalysisdetail_set-MIN_NUM_FORMS':1,
            'appsendsamplesforanalysisdetail_set-MAX_NUM_FORMS':1000,
            'appsendsamplesforanalysisdetail_set-0-sample_type':'type',
            'appsendsamplesforanalysisdetail_set-0-sample_weight':100,
            'appsendsamplesforanalysisdetail_set-0-sample_packing_type':'packing1',            
            'appsendsamplesforanalysisdetail_set-0-sample_analysis_type':'analysis1',            
            'appsendsamplesforanalysisdetail_set-0-sample_analysis_cause':'cause here',                        
    }

