from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppRemoveArea
from ..views import AppRemoveAreaListView,AppRemoveAreaReadonlyView

class AppRemoveAreaTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppRemoveAreaListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_remove_area_list'
    list_url_path = '/app_remove_area/'
    list_html_contain_ar = ['قائمة طلبات تنازل عن مساحة']
    list_html_contain_en = ['List of area assignment']

    show_view_class = AppRemoveAreaReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_remove_area_show'
    show_url_path = '/app_remove_area/%d/show/'
    show_html_contain_ar = ['عرض طلب تنازل عن مساحة']
    show_html_contain_en = ['Show area assignment']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_remove_area_add'
    add_url_path = '/app_remove_area/add/'
    add_html_contain_ar = ['اضافة طلب تنازل عن مساحة']
    add_html_contain_en = ['Add area assignment application']

    add_model = AppRemoveArea
    add_data = {
            'remove_type':'first',
            'area_in_km2':15,
            'area_percent_from_total':100,
    }
    add_file_data = ['geo_coordinator_for_removed_area_file','geo_coordinator_for_remain_area_file','map_for_clarification_file','technical_report_for_removed_area_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

