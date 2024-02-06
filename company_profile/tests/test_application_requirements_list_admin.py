from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppRequirementsList

class AppRequirementsListAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppRequirementsList
    change_data = {
            'apprequirementslistmangamequipments_set-TOTAL_FORMS':1,
            'apprequirementslistmangamequipments_set-INITIAL_FORMS':0,
            'apprequirementslistmangamequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistmangamequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistmangamequipments_set-0-item':'abc',
            'apprequirementslistmangamequipments_set-0-description':'abc desc',
            'apprequirementslistmangamequipments_set-0-qty':5,            

            'apprequirementslistfactoryequipments_set-TOTAL_FORMS':1,
            'apprequirementslistfactoryequipments_set-INITIAL_FORMS':0,
            'apprequirementslistfactoryequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistfactoryequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistfactoryequipments_set-0-item':'abc',
            'apprequirementslistfactoryequipments_set-0-description':'abc desc',
            'apprequirementslistfactoryequipments_set-0-qty':5,            

            'apprequirementslistelectricityequipments_set-TOTAL_FORMS':1,
            'apprequirementslistelectricityequipments_set-INITIAL_FORMS':0,
            'apprequirementslistelectricityequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistelectricityequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistelectricityequipments_set-0-item':'abc',
            'apprequirementslistelectricityequipments_set-0-description':'abc desc',
            'apprequirementslistelectricityequipments_set-0-qty':5,            

            'apprequirementslistchemicallabequipments_set-TOTAL_FORMS':1,
            'apprequirementslistchemicallabequipments_set-INITIAL_FORMS':0,
            'apprequirementslistchemicallabequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistchemicallabequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistchemicallabequipments_set-0-item':'abc',
            'apprequirementslistchemicallabequipments_set-0-description':'abc desc',
            'apprequirementslistchemicallabequipments_set-0-qty':5,            

            'apprequirementslistchemicalequipments_set-TOTAL_FORMS':1,
            'apprequirementslistchemicalequipments_set-INITIAL_FORMS':0,
            'apprequirementslistchemicalequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistchemicalequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistchemicalequipments_set-0-item':'abc',
            'apprequirementslistchemicalequipments_set-0-description':'abc desc',
            'apprequirementslistchemicalequipments_set-0-qty':5,            

            'apprequirementslistmotafjeratequipments_set-TOTAL_FORMS':1,
            'apprequirementslistmotafjeratequipments_set-INITIAL_FORMS':0,
            'apprequirementslistmotafjeratequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistmotafjeratequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistmotafjeratequipments_set-0-item':'abc',
            'apprequirementslistmotafjeratequipments_set-0-description':'abc desc',
            'apprequirementslistmotafjeratequipments_set-0-qty':5,            

            'apprequirementslistvehiclesequipments_set-TOTAL_FORMS':1,
            'apprequirementslistvehiclesequipments_set-INITIAL_FORMS':0,
            'apprequirementslistvehiclesequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistvehiclesequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistvehiclesequipments_set-0-item':'abc',
            'apprequirementslistvehiclesequipments_set-0-description':'abc desc',
            'apprequirementslistvehiclesequipments_set-0-qty':5,            
    }

