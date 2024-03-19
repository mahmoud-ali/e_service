from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppFuelPermission

class AppFuelPermissionAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppFuelPermission
    change_data = {
            'appfuelpermissiondetail_set-TOTAL_FORMS':1,
            'appfuelpermissiondetail_set-INITIAL_FORMS':0,
            'appfuelpermissiondetail_set-MIN_NUM_FORMS':1,
            'appfuelpermissiondetail_set-MAX_NUM_FORMS':1000,
            'appfuelpermissiondetail_set-0-fuel_type_name':'aaa',
            'appfuelpermissiondetail_set-0-fuel_qty':32,
    }

