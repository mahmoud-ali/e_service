from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppForeignerProcedure
from ..views import AppForeignerProcedureListView,AppForeignerProcedureReadonlyView

class AppForeignerProcedureTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppForeignerProcedureListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_foreigner_procedure_list'
    list_url_path = '/app_foreigner_procedure/'
    list_html_contain_ar = ['قائمة طلبات اجراءات الاجانب']
    list_html_contain_en = ['List of foreigner procedures']

    show_view_class = AppForeignerProcedureReadonlyView
    show_template_name = 'company_profile/application_readonly_master_details.html'
    show_url_name = 'profile:app_foreigner_procedure_show'
    show_url_path = '/app_foreigner_procedure/%d/show/'
    show_html_contain_ar = ['عرض طلب اجراءات اجانب']
    show_html_contain_en = ['Show foreigner procedure']

    add_template_name = 'company_profile/application_add_master_details.html'
    add_url_name = 'profile:app_foreigner_procedure_add'
    add_url_path = '/app_foreigner_procedure/add/'
    add_html_contain_ar = ['اضافة طلب اجراءات اجانب']
    add_html_contain_en = ['Add foreigner procedure']

    add_model = AppForeignerProcedure
    add_data = {
            'procedure_type':1,
            'procedure_from':'2024-02-01',
            'procedure_to':'2024-02-15',
            'procedure_cause':'cause here',
            'appforeignerproceduredetail_set-TOTAL_FORMS':1,
            'appforeignerproceduredetail_set-INITIAL_FORMS':0,
            'appforeignerproceduredetail_set-MIN_NUM_FORMS':1,
            'appforeignerproceduredetail_set-MAX_NUM_FORMS':1000,
            'appforeignerproceduredetail_set-0-employee_name':'abc',
            'appforeignerproceduredetail_set-0-employee_address':'123',
    }
    add_file_data = ['official_letter_file','passport_file','cv_file','experience_certificates_file','eqama_file','dawa_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

