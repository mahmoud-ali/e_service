from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppImportPermission
from ..views import AppImportPermissionListView,AppImportPermissionReadonlyView

class AppImportPermissionTests(ProCompanyTests,TestCase):
    #username = "bbb"

    list_view_class = AppImportPermissionListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_import_permission_list'
    list_url_path = '/app_import_permission/'
    list_html_contain_ar = ['قائمة طلبات اذن ادخال مواد']
    list_html_contain_en = ['List of Import Permissions']

    show_view_class = AppImportPermissionReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_import_permission_show'
    show_url_path = '/app_import_permission/%d/show/'
    show_html_contain_ar = ['عرض اذن ادخال مواد']
    show_html_contain_en = ['Show Import Permission']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_import_permission_add'
    add_url_path = '/app_import_permission/add/'
    add_html_contain_ar = ['اضافة طلب اذن ادخال مواد']
    add_html_contain_en = ['Add Import Permission']

    add_model = AppImportPermission
    add_data = {
    }
    add_file_data = ['attachement_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

