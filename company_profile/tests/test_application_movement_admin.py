from django.test import TestCase
from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppForignerMovement

class AppMovementAdminTests(ProCompanyAdminTests,TestCase):
    username = "admin"

    admin_accepted_email_subject_contain_ar = ['تم استلام الطلب']
    admin_accepted_email_subject_contain_en = ['Application accepted']
    admin_approved_email_subject_contain_ar = ['تم تصديق الطلب']
    admin_approved_email_subject_contain_en = ['Application approved']
    admin_rejected_email_subject_contain_ar = ['تم رفض الطلب']
    admin_rejected_email_subject_contain_en = ['Application rejected']

    admin_accepted_email_body_template_ar = 'company_profile/email/accepted_email_ar.html'
    admin_accepted_email_body_template_en = 'company_profile/email/accepted_email_en.html'
    admin_approved_email_body_template_ar = 'company_profile/email/approved_email_ar.html'
    admin_approved_email_body_template_en = 'company_profile/email/approved_email_en.html'
    admin_rejected_email_body_template_ar = 'company_profile/email/rejected_email_ar.html'
    admin_rejected_email_body_template_en = 'company_profile/email/rejected_email_en.html'

    change_model = AppForignerMovement
    change_data = {
            'route_from':'CCCCCCC',
            'route_to':'DDDDDDD',
            'period_from':'2024-01-05',
            'period_to':'2024-02-28',
            'address_in_sudan':'Omdurman',
            'nationality':1,
            'passport_no':'4588854',
            'passport_expiry_date':'2024-12-31',
    }

