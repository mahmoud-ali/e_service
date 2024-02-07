from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppExportGoldRaw

class AppExportGoldRawAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppExportGoldRaw
    change_data = {
            'mineral':1,
            'license_type':'license1',
            'amount_in_gram':5,
            'sale_price':5,
            'export_country':'Egypt',
            'export_city':'Cairo',
            'export_address':'street 12',
    }

