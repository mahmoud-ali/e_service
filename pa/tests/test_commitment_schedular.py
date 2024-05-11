from django.test import TestCase
from django.urls import reverse

from pa.models import TblCompanyCommitmentMaster, TblCompanyCommitmentSchedular
from pa.views.commitment_schedular import TblCompanyCommitmentScheduleCreateView, TblCompanyCommitmentScheduleDeleteView, TblCompanyCommitmentScheduleListView, TblCompanyCommitmentScheduleReadonlyView, TblCompanyCommitmentScheduleUpdateView

from .common import CommonViewTests

class CommitmentSchedularViewTests(CommonViewTests,TestCase):
    list_view_class = TblCompanyCommitmentScheduleListView 
    list_template_name = 'pa/application_list.html'
    list_url_name = 'pa:commitment_schedule_list'

    add_view_class = TblCompanyCommitmentScheduleCreateView
    add_template_name = 'pa/application_add.html'
    add_url_name = 'pa:commitment_schedule_add'
    add_model = TblCompanyCommitmentSchedular
    add_data = {
        'commitment':40,
        'request_interval':TblCompanyCommitmentSchedular.INTERVAL_TYPE_YEAR,
        'request_next_interval_dt':'2031-05-05',
     }
    add_file_data = []

    show_view_class = TblCompanyCommitmentScheduleReadonlyView
    show_template_name = 'pa/application_readonly_master_details.html'
    show_url_name = 'pa:commitment_schedule_show'

    update_view_class = TblCompanyCommitmentScheduleUpdateView
    update_template_name = 'pa/application_add.html'
    update_url_name = 'pa:commitment_schedule_edit'

    delete_view_class = TblCompanyCommitmentScheduleDeleteView
    delete_template_name = 'pa/application_delete.html'
    delete_url_name = 'pa:commitment_schedule_delete'

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
