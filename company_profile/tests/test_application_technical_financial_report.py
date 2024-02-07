from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppTechnicalFinancialReport
from ..views import AppTechnicalFinancialReportListView,AppTechnicalFinancialReportReadonlyView

class AppTechnicalFinancialReportTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppTechnicalFinancialReportListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_technical_financial_report_list'
    list_url_path = '/app_technical_financial_report/'
    list_html_contain_ar = ['قائمة طلبات التقارير الفنية والمالية']
    list_html_contain_en = ['List of technical','Financial Reports']

    show_view_class = AppTechnicalFinancialReportReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_technical_financial_report_show'
    show_url_path = '/app_technical_financial_report/%d/show/'
    show_html_contain_ar = ['عرض طلب تقرير فني ومالي']
    show_html_contain_en = ['Show technical','financial report']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_technical_financial_report_add'
    add_url_path = '/app_technical_financial_report/add/'
    add_html_contain_ar = ['اضافة طلب تقرير فني ومالي']
    add_html_contain_en = ['Add new technical','financial report']

    add_model = AppTechnicalFinancialReport
    add_data = {
            'report_from':'2024-02-02',
            'report_to':'2024-02-06',
            'report_type':'technical',
            'report_comments':'comments here',
    }
    add_file_data = ['report_file','other_attachments_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

