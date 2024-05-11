from django.test import TestCase
from django.urls import reverse

from company_profile.models import TblCompanyProduction
from pa.models import TblCompanyCommitmentMaster
from pa.views.commitment import TblCompanyCommitmentCreateView, TblCompanyCommitmentDeleteView, TblCompanyCommitmentListView, TblCompanyCommitmentReadonlyView, TblCompanyCommitmentUpdateView

from .common import CommonViewTests

class CommitmentViewTests(CommonViewTests,TestCase):
    list_view_class = TblCompanyCommitmentListView 
    list_template_name = 'pa/application_list.html'
    list_url_name = 'pa:commitment_list'

    add_view_class = TblCompanyCommitmentCreateView
    add_template_name = 'pa/application_add_master_details.html'
    add_url_name = 'pa:commitment_add'
    add_model = TblCompanyCommitmentMaster
    add_data = {
        'company':10,
        'license':8,
        'currency':'euro',
        'tblcompanycommitmentdetail_set-TOTAL_FORMS':1,
        'tblcompanycommitmentdetail_set-INITIAL_FORMS':0,
        'tblcompanycommitmentdetail_set-MIN_NUM_FORMS':1,
        'tblcompanycommitmentdetail_set-MAX_NUM_FORMS':1000,
        'tblcompanycommitmentdetail_set-0-item':1,
        'tblcompanycommitmentdetail_set-0-amount_factor':10,
     }
    add_file_data = []

    show_view_class = TblCompanyCommitmentReadonlyView
    show_template_name = 'pa/application_readonly_master_details.html'
    show_url_name = 'pa:commitment_show'

    update_view_class = TblCompanyCommitmentUpdateView
    update_template_name = 'pa/application_add_master_details.html'
    update_url_name = 'pa:commitment_edit'

    delete_view_class = TblCompanyCommitmentDeleteView
    delete_template_name = 'pa/application_delete_master_detail.html'
    delete_url_name = 'pa:commitment_delete'

    invalid_data = {}

    choose_template = 'pa/application_choose.html'

    def test_add_status_code(self):
        model = TblCompanyProduction.objects.first()
        url = reverse(self.add_url_name)+'?company={0}'.format(model.id)
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_add_view_used(self):
        model = TblCompanyProduction.objects.first()
        url = reverse(self.add_url_name)+'?company={0}'.format(model.id)
        self.response = self.client.get(url)
        self.assertIs(self.response.resolver_match.func.view_class, self.add_view_class)

    def test_add_template_used(self):
        model = TblCompanyProduction.objects.first()
        url = reverse(self.add_url_name)+'?company={0}'.format(model.id)
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, self.add_template_name)

    def test_add_invalid_company_not_found(self):
        url = reverse(self.add_url_name)+'?company=0'
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 404)

    def test_add_show_choose_template_to_select_company(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, self.choose_template)
