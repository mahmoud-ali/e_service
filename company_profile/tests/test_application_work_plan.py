from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppWorkPlan
from ..views import AppWorkPlanListView,AppWorkPlanReadonlyView

class AppWorkPlanTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppWorkPlanListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_work_plan_list'
    list_url_path = '/app_work_plan/'
    list_html_contain_ar = ['قائمة طلبات خطة عمل']
    list_html_contain_en = ['List of work plans']

    show_view_class = AppWorkPlanReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_work_plan_show'
    show_url_path = '/app_work_plan/%d/show/'
    show_html_contain_ar = ['عرض طلب خطة عمل']
    show_html_contain_en = ['Show work plan']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_work_plan_add'
    add_url_path = '/app_work_plan/add/'
    add_html_contain_ar = ['اضافة طلب خطة عمل']
    add_html_contain_en = ['Add new work plan']

    add_model = AppWorkPlan
    add_data = {
            'plan_from':'2024-02-02',
            'plan_to':'2024-02-06',
    }
    add_file_data = ['official_letter_file','work_plan_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

