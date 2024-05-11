from django.test import TestCase
from django.urls import reverse

from pa.models import TblCompanyRequestMaster,TblCompanyPaymentMaster
from pa.views.payment import TblCompanyPaymentCreateView, TblCompanyPaymentDeleteView, TblCompanyPaymentListView, TblCompanyPaymentReadonlyView, TblCompanyPaymentUpdateView

from .common import CommonViewTests

class PaymentViewTests(CommonViewTests,TestCase):
    list_view_class = TblCompanyPaymentListView 
    list_template_name = 'pa/application_list.html'
    list_url_name = 'pa:payment_list'

    add_view_class = TblCompanyPaymentCreateView
    add_template_name = 'pa/application_add_master_details.html'
    add_url_name = 'pa:payment_add'
    add_model = TblCompanyPaymentMaster
    add_data = {
        'request':20,
        'payment_dt':'2033-05-05',
        'currency':'euro',
        'exchange_rate':1,
        'tblcompanypaymentdetail_set-TOTAL_FORMS':1,
        'tblcompanypaymentdetail_set-INITIAL_FORMS':0,
        'tblcompanypaymentdetail_set-MIN_NUM_FORMS':1,
        'tblcompanypaymentdetail_set-MAX_NUM_FORMS':1000,
        'tblcompanypaymentdetail_set-0-item':1,
        'tblcompanypaymentdetail_set-0-amount':1000,
        'tblcompanypaymentmethod_set-TOTAL_FORMS':1,
        'tblcompanypaymentmethod_set-INITIAL_FORMS':0,
        'tblcompanypaymentmethod_set-MIN_NUM_FORMS':1,
        'tblcompanypaymentmethod_set-MAX_NUM_FORMS':1000,
        'tblcompanypaymentmethod_set-0-amount':1000,
        'tblcompanypaymentmethod_set-0-method':1,
        'tblcompanypaymentmethod_set-0-ref_key':1,
     }
    add_file_data = [
        'exchange_attachement_file',
        'tblcompanypaymentdetail_set-0-attachement_file',
        'tblcompanypaymentmethod_set-0-attachement_file',
    ]

    show_view_class = TblCompanyPaymentReadonlyView
    show_template_name = 'pa/application_readonly_master_details.html'
    show_url_name = 'pa:payment_show'

    update_view_class = TblCompanyPaymentUpdateView
    update_template_name = 'pa/application_add_master_details.html'
    update_url_name = 'pa:payment_edit'

    delete_view_class = TblCompanyPaymentDeleteView
    delete_template_name = 'pa/application_delete_master_detail.html'
    delete_url_name = 'pa:payment_delete'

    invalid_data = {
        'request':20,
    }

    choose_template = 'pa/application_choose.html'

    def test_add_status_code(self):
        model = TblCompanyRequestMaster.objects.first()
        url = reverse(self.add_url_name)+'?request={0}'.format(model.id)
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_add_view_used(self):
        model = TblCompanyRequestMaster.objects.first()
        url = reverse(self.add_url_name)+'?request={0}'.format(model.id)
        self.response = self.client.get(url)
        self.assertIs(self.response.resolver_match.func.view_class, self.add_view_class)

    def test_add_template_used(self):
        model = TblCompanyRequestMaster.objects.first()
        url = reverse(self.add_url_name)+'?request={0}'.format(model.id)
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, self.add_template_name)

    def test_add_invalid_request_not_found(self):
        url = reverse(self.add_url_name)+'?request=0'
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 404)

    def test_add_show_choose_template_to_select_request(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, self.choose_template)
