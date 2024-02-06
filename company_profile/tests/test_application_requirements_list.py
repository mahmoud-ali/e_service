from django.test import TestCase

from .pro_company_tests import ProCompanyTests

from ..models import AppRequirementsList
from ..views import AppRequirementsListListView,AppRequirementsListReadonlyView

class AppRequirementsListTests(ProCompanyTests,TestCase):
    username = "admin"

    list_view_class = AppRequirementsListListView 
    list_template_name = 'company_profile/application_list.html'
    list_context_object_name = "apps"
    list_url_name = 'profile:app_requirements_list_list'
    list_url_path = '/app_requirements_list/'
    list_html_contain_ar = ['قائمة طلبات كشف الاحتياجات']
    list_html_contain_en = ['List of Requirements List']

    show_view_class = AppRequirementsListReadonlyView
    show_template_name = 'company_profile/views/requirements_list_readonly_master_details.html'
    show_url_name = 'profile:app_requirements_list_show'
    show_url_path = '/app_requirements_list/%d/show/'
    show_html_contain_ar = ['عرض طلب كشف احتياجات']
    show_html_contain_en = ['Show Requirements List']

    add_template_name = 'company_profile/views/requirements_list_add_master_details.html'
    add_url_name = 'profile:app_requirements_list_add'
    add_url_path = '/app_requirements_list/add/'
    add_html_contain_ar = ['اضافة طلب كشف احتياجات']
    add_html_contain_en = ['Add Requirements List']

    add_model = AppRequirementsList
    add_data = {
            'apprequirementslistmangamequipments_set-TOTAL_FORMS':1,
            'apprequirementslistmangamequipments_set-INITIAL_FORMS':0,
            'apprequirementslistmangamequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistmangamequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistmangamequipments_set-0-item':'abc',
            'apprequirementslistmangamequipments_set-0-description':'abc desc',
            'apprequirementslistmangamequipments_set-0-qty':5,            

            'apprequirementslistfactoryequipments_set-TOTAL_FORMS':1,
            'apprequirementslistfactoryequipments_set-INITIAL_FORMS':0,
            'apprequirementslistfactoryequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistfactoryequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistfactoryequipments_set-0-item':'abc',
            'apprequirementslistfactoryequipments_set-0-description':'abc desc',
            'apprequirementslistfactoryequipments_set-0-qty':5,            

            'apprequirementslistelectricityequipments_set-TOTAL_FORMS':1,
            'apprequirementslistelectricityequipments_set-INITIAL_FORMS':0,
            'apprequirementslistelectricityequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistelectricityequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistelectricityequipments_set-0-item':'abc',
            'apprequirementslistelectricityequipments_set-0-description':'abc desc',
            'apprequirementslistelectricityequipments_set-0-qty':5,            

            'apprequirementslistchemicallabequipments_set-TOTAL_FORMS':1,
            'apprequirementslistchemicallabequipments_set-INITIAL_FORMS':0,
            'apprequirementslistchemicallabequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistchemicallabequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistchemicallabequipments_set-0-item':'abc',
            'apprequirementslistchemicallabequipments_set-0-description':'abc desc',
            'apprequirementslistchemicallabequipments_set-0-qty':5,            

            'apprequirementslistchemicalequipments_set-TOTAL_FORMS':1,
            'apprequirementslistchemicalequipments_set-INITIAL_FORMS':0,
            'apprequirementslistchemicalequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistchemicalequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistchemicalequipments_set-0-item':'abc',
            'apprequirementslistchemicalequipments_set-0-description':'abc desc',
            'apprequirementslistchemicalequipments_set-0-qty':5,            

            'apprequirementslistmotafjeratequipments_set-TOTAL_FORMS':1,
            'apprequirementslistmotafjeratequipments_set-INITIAL_FORMS':0,
            'apprequirementslistmotafjeratequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistmotafjeratequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistmotafjeratequipments_set-0-item':'abc',
            'apprequirementslistmotafjeratequipments_set-0-description':'abc desc',
            'apprequirementslistmotafjeratequipments_set-0-qty':5,            

            'apprequirementslistvehiclesequipments_set-TOTAL_FORMS':1,
            'apprequirementslistvehiclesequipments_set-INITIAL_FORMS':0,
            'apprequirementslistvehiclesequipments_set-MIN_NUM_FORMS':1,
            'apprequirementslistvehiclesequipments_set-MAX_NUM_FORMS':1000,
            'apprequirementslistvehiclesequipments_set-0-item':'abc',
            'apprequirementslistvehiclesequipments_set-0-description':'abc desc',
            'apprequirementslistvehiclesequipments_set-0-qty':5,            
    }
    add_file_data = ['approved_work_plan_file','initial_voucher_file','specifications_file','mshobat_jamarik_file']

    add_email_subject_contain_ar = ['تم ارسال طلب جديد']
    add_email_subject_contain_en = ['New application submitted']
    add_email_body_template_ar = 'company_profile/email/submitted_email_ar.html'
    add_email_body_template_en = 'company_profile/email/submitted_email_en.html'

