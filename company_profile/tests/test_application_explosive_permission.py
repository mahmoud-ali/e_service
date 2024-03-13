from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppExplosivePermission
from ..views import AppExplosivePermissionListView,AppExplosivePermissionReadonlyView

class AppExplosivePermissionTests(ProCompanyTests,TestCase):
    #username = "bbb"

    list_view_class = AppExplosivePermissionListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_explosive_permission_list'
    list_url_path = '/app_explosive_permission/'
    list_html_contain_ar = ['قائمة طلبات تجديد اذن استخدام متفجرات']
    list_html_contain_en = ['List of Explosive Permissions']

    show_view_class = AppExplosivePermissionReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_explosive_permission_show'
    show_url_path = '/app_explosive_permission/%d/show/'
    show_html_contain_ar = ['عرض طلب تجديد اذن استخدام متفجرات']
    show_html_contain_en = ['Show Explosive Permission']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_explosive_permission_add'
    add_url_path = '/app_explosive_permission/add/'
    add_html_contain_ar = ['اضافة طلب تجديد اذن استخدام متفجرات']
    add_html_contain_en = ['Add Explosive Permission']

    add_model = AppExplosivePermission
    add_data = {
    }
    add_file_data = ['attachement_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

