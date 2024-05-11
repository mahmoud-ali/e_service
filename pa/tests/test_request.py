from django.test import TestCase
from django.urls import reverse

from pa.models import TblCompanyCommitmentMaster, TblCompanyRequestMaster
from pa.views.request import TblCompanyRequestCreateView, TblCompanyRequestDeleteView, TblCompanyRequestListView, TblCompanyRequestReadonlyView, TblCompanyRequestUpdateView

from .common import CommonViewTests

class RequestViewTests(CommonViewTests,TestCase):
    list_view_class = TblCompanyRequestListView 
    list_template_name = 'pa/application_list.html'
    list_url_name = 'pa:request_list'

    add_view_class = TblCompanyRequestCreateView
    add_template_name = 'pa/application_add_master_details.html'
    add_url_name = 'pa:request_add'
    add_model = TblCompanyRequestMaster
    add_data = {
        'commitment':37,
        'from_dt':'2029-05-05',
        'to_dt':'2030-05-04',
        'currency':'euro',
        'tblcompanyrequestdetail_set-TOTAL_FORMS':1,
        'tblcompanyrequestdetail_set-INITIAL_FORMS':0,
        'tblcompanyrequestdetail_set-MIN_NUM_FORMS':1,
        'tblcompanyrequestdetail_set-MAX_NUM_FORMS':1000,
        'tblcompanyrequestdetail_set-0-item':1,
        'tblcompanyrequestdetail_set-0-amount':150000,
     }
    add_file_data = [
        'tblcompanyrequestdetail_set-0-attachement_file',
    ]

    show_view_class = TblCompanyRequestReadonlyView
    show_template_name = 'pa/application_readonly_master_details.html'
    show_url_name = 'pa:request_show'

    update_view_class = TblCompanyRequestUpdateView
    update_template_name = 'pa/application_add_master_details.html'
    update_url_name = 'pa:request_edit'

    delete_view_class = TblCompanyRequestDeleteView
    delete_template_name = 'pa/application_delete_master_detail.html'
    delete_url_name = 'pa:request_delete'

    invalid_data = {
        'commitment':37,
    }

    choose_template = 'pa/application_choose.html'

    def test_add_status_code(self):
        model = TblCompanyCommitmentMaster.objects.first()
        url = reverse(self.add_url_name)+'?commitment={0}'.format(model.id)
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_add_view_used(self):
        model = TblCompanyCommitmentMaster.objects.first()
        url = reverse(self.add_url_name)+'?commitment={0}'.format(model.id)
        self.response = self.client.get(url)
        self.assertIs(self.response.resolver_match.func.view_class, self.add_view_class)

    def test_add_template_used(self):
        model = TblCompanyCommitmentMaster.objects.first()
        url = reverse(self.add_url_name)+'?commitment={0}'.format(model.id)
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, self.add_template_name)

    def test_add_invalid_commitment_not_found(self):
        url = reverse(self.add_url_name)+'?commitment=0'
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 404)

    def test_add_show_choose_template_to_select_commitment(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, self.choose_template)
