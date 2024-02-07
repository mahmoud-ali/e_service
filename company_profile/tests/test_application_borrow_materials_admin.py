from django.test import TestCase
from .pro_company_admin_tests import ProCompanyAdminTests

from ..models import AppBorrowMaterial

class AppBorrowMaterialAdminTests(ProCompanyAdminTests,TestCase):
    #username = "admin"

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

    change_model = AppBorrowMaterial
    change_data = {
            'company_from':2,
            'borrow_date':'2024-01-01',
            'appborrowmaterialdetail_set-TOTAL_FORMS':1,
            'appborrowmaterialdetail_set-INITIAL_FORMS':0,
            'appborrowmaterialdetail_set-MIN_NUM_FORMS':1,
            'appborrowmaterialdetail_set-MAX_NUM_FORMS':1000,
            'appborrowmaterialdetail_set-0-material':'Golden tool',
            'appborrowmaterialdetail_set-0-quantity':1,            
    }

