from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppReexportEquipments
from ..views import AppReexportEquipmentsListView,AppReexportEquipmentsReadonlyView

class AppReexportEquipmentsTests(ProCompanyTests,TestCase):
    #username = "admin"

    list_view_class = AppReexportEquipmentsListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_reexport_equipments_list'
    list_url_path = '/app_reexport_equipments/'
    list_html_contain_ar = ['قائمة طلبات اعادة صادر لاليات ومعدات']
    list_html_contain_en = ['List of Reexport of Machinery and Equipments']

    show_view_class = AppReexportEquipmentsReadonlyView
    show_template_name = 'company_profile/application_readonly_master_details.html'
    show_url_name = 'profile:app_reexport_equipments_show'
    show_url_path = '/app_reexport_equipments/%d/show/'
    show_html_contain_ar = ['عرض طلب اعادة صادر لاليات ومعدات']
    show_html_contain_en = ['Show Reexport of Machinery and Equipments']

    add_template_name = 'company_profile/application_add_master_details.html'
    add_url_name = 'profile:app_reexport_equipments_add'
    add_url_path = '/app_reexport_equipments/add/'
    add_html_contain_ar = ['اضافة طلب اعادة صادر لاليات ومعدات']
    add_html_contain_en = ['Add Reexport of Machinery and Equipments']

    add_model = AppReexportEquipments
    add_data = {
            'cause_for_equipments':'cause here',
            'appreexportequipmentsdetail_set-TOTAL_FORMS':1,
            'appreexportequipmentsdetail_set-INITIAL_FORMS':0,
            'appreexportequipmentsdetail_set-MIN_NUM_FORMS':1,
            'appreexportequipmentsdetail_set-MAX_NUM_FORMS':1000,
            'appreexportequipmentsdetail_set-0-name':'abc',
            'appreexportequipmentsdetail_set-0-serial_id':'123',
            'appreexportequipmentsdetail_set-0-policy_no':'123',            
            'appreexportequipmentsdetail_set-0-voucher_no':'123',            
            'appreexportequipmentsdetail_set-0-insurance_no':'123',
            'appreexportequipmentsdetail_set-0-check_certificate_no':'123',  
    }
    add_file_data = ['shipping_policy_file','voucher_file','specifications_file','momentary_approval_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

