from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppVisibityStudy
from ..views import AppVisibityStudyListView,AppVisibityStudyReadonlyView

class AppVisibityStudyTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppVisibityStudyListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_visibility_study_list'
    list_url_path = '/app_visibility_study/'
    list_html_contain_ar = ['قائمة طلبات دراسة الجدوى']
    list_html_contain_en = ['List of Visibity Studies']

    show_view_class = AppVisibityStudyReadonlyView
    show_template_name = 'company_profile/application_readonly_master_details.html'
    show_url_name = 'profile:app_visibility_study_show'
    show_url_path = '/app_visibility_study/%d/show/'
    show_html_contain_ar = ['عرض طلب دراسة جدوى']
    show_html_contain_en = ['Show Visibity Study']

    add_template_name = 'company_profile/application_add_master_details.html'
    add_url_name = 'profile:app_visibility_study_add'
    add_url_path = '/app_visibility_study/add/'
    add_html_contain_ar = ['اضافة طلب دراسة']
    add_html_contain_en = ['Add Visibity Study']

    add_model = AppVisibityStudy
    add_data = {
            'license_type':2,
            'study_area':'area',
            'study_type':'type1',
            'study_comment':'comments',
            'appvisibitystudydetail_set-TOTAL_FORMS':1,
            'appvisibitystudydetail_set-INITIAL_FORMS':0,
            'appvisibitystudydetail_set-MIN_NUM_FORMS':1,
            'appvisibitystudydetail_set-MAX_NUM_FORMS':1000,
            'appvisibitystudydetail_set-0-study_point_id':1,
            'appvisibitystudydetail_set-0-study_point_long':32.2131231,
            'appvisibitystudydetail_set-0-study_point_lat':15.34534534,
    }
    add_file_data = ['attachement_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

