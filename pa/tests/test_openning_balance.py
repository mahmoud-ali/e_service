from django.test import TestCase
from django.urls import reverse

from pa.models import TblCompanyOpenningBalanceMaster
from pa.views.openning_balance import TblCompanyOpenningBalanceCreateView, TblCompanyOpenningBalanceDeleteView, TblCompanyOpenningBalanceListView, TblCompanyOpenningBalanceReadonlyView, TblCompanyOpenningBalanceUpdateView

from .common import CommonViewTests

class OpenningBalanceViewTests(CommonViewTests,TestCase):
    list_view_class = TblCompanyOpenningBalanceListView 
    list_template_name = 'pa/application_list.html'
    list_url_name = 'pa:openning_balance_list'

    add_view_class = TblCompanyOpenningBalanceCreateView
    add_template_name = 'pa/application_add_master_details.html'
    add_url_name = 'pa:openning_balance_add'
    add_model = TblCompanyOpenningBalanceMaster
    add_data = {
        'company':10,
        'currency':'euro',
        'tblcompanyopenningbalancedetail_set-TOTAL_FORMS':1,
        'tblcompanyopenningbalancedetail_set-INITIAL_FORMS':0,
        'tblcompanyopenningbalancedetail_set-MIN_NUM_FORMS':1,
        'tblcompanyopenningbalancedetail_set-MAX_NUM_FORMS':1000,
        'tblcompanyopenningbalancedetail_set-0-item':1,
        'tblcompanyopenningbalancedetail_set-0-amount':10,
     }
    add_file_data = []

    show_view_class = TblCompanyOpenningBalanceReadonlyView
    show_template_name = 'pa/application_readonly_master_details.html'
    show_url_name = 'pa:openning_balance_show'

    update_view_class = TblCompanyOpenningBalanceUpdateView
    update_template_name = 'pa/application_add_master_details.html'
    update_url_name = 'pa:openning_balance_edit'

    delete_view_class = TblCompanyOpenningBalanceDeleteView
    delete_template_name = 'pa/application_delete_master_detail.html'
    delete_url_name = 'pa:openning_balance_delete'

    invalid_data = {}
