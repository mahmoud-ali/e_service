from django.test import TestCase

from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppCyanideCertificate

class AppCyanideCertificateAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

    change_model = AppCyanideCertificate
    change_data = {
    }

