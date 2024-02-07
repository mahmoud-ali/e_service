from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppExportGold

class AppExportGoldAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    change_model = AppExportGold
    change_data = {
            'total_in_gram':50,
            'net_in_gram':40,
            'zakat_in_gram':5,
            'awaad_jalila_in_gram':5,
            'arbah_amal_in_gram':5,
            'sold_for_bank_of_sudan_in_gram':4,
            'amount_to_export_in_gram':3,
            'remain_in_gram':10,
    }

