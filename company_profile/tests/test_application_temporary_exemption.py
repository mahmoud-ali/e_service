from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppTemporaryExemption
from ..views import AppTemporaryExemptionListView,AppTemporaryExemptionReadonlyView

class AppTemporaryExemptionTests(ProCompanyTests,TestCase):
    #username = "bbb"

    list_view_class = AppTemporaryExemptionListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_temporary_exemption_list'
    list_url_path = '/app_temporary_exemption/'
    list_html_contain_ar = ['قائمة طلبات افراج مؤقت']
    list_html_contain_en = ['List of Temporary Exemptions']

    show_view_class = AppTemporaryExemptionReadonlyView
    show_template_name = 'company_profile/application_readonly.html'
    show_url_name = 'profile:app_temporary_exemption_show'
    show_url_path = '/app_temporary_exemption/%d/show/'
    show_html_contain_ar = ['عرض طلب افراج مؤقت']
    show_html_contain_en = ['Show Temporary Exemptions']

    add_template_name = 'company_profile/application_add.html'
    add_url_name = 'profile:app_temporary_exemption_add'
    add_url_path = '/app_temporary_exemption/add/'
    add_html_contain_ar = ['اضافة طلب افراج مؤقت']
    add_html_contain_en = ['Add Temporary Exemptions']

    add_model = AppTemporaryExemption
    add_data = {
    }
    add_file_data = ['attachement_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

