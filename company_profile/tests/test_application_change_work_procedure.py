from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppChangeWorkProcedure
from ..views import AppChangeWorkProcedureListView,AppChangeWorkProcedureReadonlyView

class AppChangeWorkProcedureTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppChangeWorkProcedureListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_change_work_procedure_list'
    list_url_path = '/app_change_work_procedure/'
    list_html_contain_ar = ['قائمة تغيير طريقة العمل']
    list_html_contain_en = ['List of change work procedure']

    show_view_class = AppChangeWorkProcedureReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_change_work_procedure_show'
    show_url_path = '/app_change_work_procedure/%d/show/'
    show_html_contain_ar = ['عرض طلب تغيير طريقة عمل']
    show_html_contain_en = ['Show change work procedure']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_change_work_procedure_add'
    add_url_path = '/app_change_work_procedure/add/'
    add_html_contain_ar = ['اضافة طلب تغيير طريقة عمل']
    add_html_contain_en = ['Add change work procedure']

    add_model = AppChangeWorkProcedure
    add_data = {
            'reason_for_change':'reason here',
            'purpose_for_change':'purpose here',
            'rational_reason':'cause here',
    }
    add_file_data = ['study_about_change_reason_file','study_about_new_suggestion_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

