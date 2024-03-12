from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppVisibityStudy

class AppVisibityStudyAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppVisibityStudy
    change_data = {
            'license_type':2,
            'study_area':'area',
            'study_type':'type1',
            'study_comment':'comments',
            'appvisibitystudydetail_set-TOTAL_FORMS':1,
            'appvisibitystudydetail_set-INITIAL_FORMS':0,
            'appvisibitystudydetail_set-MIN_NUM_FORMS':1,
            'appvisibitystudydetail_set-MAX_NUM_FORMS':1000,
            'appvisibitystudydetail_set-0-study_point_id':1,
            'appvisibitystudydetail_set-0-study_point_long':32.2131231,
            'appvisibitystudydetail_set-0-study_point_lat':15.34534534,
    }

