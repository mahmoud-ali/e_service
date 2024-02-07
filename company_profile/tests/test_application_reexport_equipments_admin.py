from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppReexportEquipments

class AppReexportEquipmentsAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppReexportEquipments
    change_data = {
            'cause_for_equipments':'cause here',
            'appreexportequipmentsdetail_set-TOTAL_FORMS':1,
            'appreexportequipmentsdetail_set-INITIAL_FORMS':0,
            'appreexportequipmentsdetail_set-MIN_NUM_FORMS':1,
            'appreexportequipmentsdetail_set-MAX_NUM_FORMS':1000,
            'appreexportequipmentsdetail_set-0-name':'abc',
            'appreexportequipmentsdetail_set-0-serial_id':'123',
            'appreexportequipmentsdetail_set-0-policy_no':'123',            
            'appreexportequipmentsdetail_set-0-voucher_no':'123',            
            'appreexportequipmentsdetail_set-0-insurance_no':'123',
            'appreexportequipmentsdetail_set-0-check_certificate_no':'123',  
    }

