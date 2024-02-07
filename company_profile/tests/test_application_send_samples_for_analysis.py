from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppSendSamplesForAnalysis
from ..views import AppSendSamplesForAnalysisListView,AppSendSamplesForAnalysisReadonlyView

class AppSendSamplesForAnalysisTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppSendSamplesForAnalysisListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_send_samples_for_analysis_list'
    list_url_path = '/app_send_samples_for_analysis/'
    list_html_contain_ar = ['قائمة طلبات ارسال عينات للخارج للتحليل']
    list_html_contain_en = ['List of samples for analysis']

    show_view_class = AppSendSamplesForAnalysisReadonlyView
    show_template_name = 'company_profile/application_readonly_master_details.html'
    show_url_name = 'profile:app_send_samples_for_analysis_show'
    show_url_path = '/app_send_samples_for_analysis/%d/show/'
    show_html_contain_ar = ['عرض طلب ارسال عينات للخارج للتحليل']
    show_html_contain_en = ['Show samples for analysis']

    add_template_name = 'company_profile/application_add_master_details.html'
    add_url_name = 'profile:app_send_samples_for_analysis_add'
    add_url_path = '/app_send_samples_for_analysis/add/'
    add_html_contain_ar = ['اضافة طلب ارسال عينات للخارج للتحليل']
    add_html_contain_en = ['Add samples for analysis']

    add_model = AppSendSamplesForAnalysis
    add_data = {
            'lab_country':'Egypt',
            'lab_city':'Cairo',
            'lab_address':'address here',
            'lab_analysis_cost':500,
            'appsendsamplesforanalysisdetail_set-TOTAL_FORMS':1,
            'appsendsamplesforanalysisdetail_set-INITIAL_FORMS':0,
            'appsendsamplesforanalysisdetail_set-MIN_NUM_FORMS':1,
            'appsendsamplesforanalysisdetail_set-MAX_NUM_FORMS':1000,
            'appsendsamplesforanalysisdetail_set-0-sample_type':'type',
            'appsendsamplesforanalysisdetail_set-0-sample_weight':100,
            'appsendsamplesforanalysisdetail_set-0-sample_packing_type':'packing1',            
            'appsendsamplesforanalysisdetail_set-0-sample_analysis_type':'analysis1',            
            'appsendsamplesforanalysisdetail_set-0-sample_analysis_cause':'cause here', 
    }
    add_file_data = ['last_analysis_report_file','initial_voucher_file','sample_description_form_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

