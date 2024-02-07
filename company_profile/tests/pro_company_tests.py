import io 

from django.test import RequestFactory
from django.urls import reverse, resolve
from django.conf import settings

from django.core import mail

from django.contrib.auth import get_user_model

from ..workflow import SUBMITTED,ACCEPTED,APPROVED,REJECTED

class ProCompanyTests():
    fixtures = ['test_data.yaml']

    language = ""
    username = ""

    list_view_class = None 
    list_template_name = ''
    list_context_object_name = ''
    list_url_name = ''
    list_url_path = ''
    list_html_contain = ''

    show_view_class = None
    show_template_name = ''
    show_url_name = ''
    show_url_path = ''
    show_html_contain = ''

    add_template_name = ''
    add_url_name = ''
    add_url_path = ''
    add_html_contain = ''
    add_email_subject_contain = ''
    add_email_body_contain = ''
    add_model = None
    add_data = {}
    add_file_data = []

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username=self.username)

        self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: self.language})

        self.client.force_login(self.user,settings.AUTHENTICATION_BACKENDS[0])

    def test_status_code_for_list_page(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertEqual(self.response.status_code, 200)

    def test_status_code_for_add_page(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_status_code_for_show_page(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]

        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertEqual(self.response.status_code, 200)

    def test_template_for_list_page(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertTemplateUsed(self.response, self.list_template_name)

    def test_template_for_add_page(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, self.add_template_name)

    def test_template_for_show_page(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]

        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertTemplateUsed(self.response, self.show_template_name)

    def test_contains_correct_html_for_list_page(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertContains(self.response, self.list_html_contain)

    def test_contains_correct_html_for_add_page(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertContains(self.response, self.add_html_contain)

    def test_contains_correct_html_for_show_page(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]

        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)            
            self.assertContains(self.response, self.show_html_contain)

    def test_model_has_get_absolute_url_func(self):
        model = self.add_model.objects.first()
        self.assertTrue(hasattr(model,'get_absolute_url')) #model implement get_absolute_url

    def test_model_get_absolute_url_return_correct_url(self):
        model = self.add_model.objects.first()
        url = reverse(self.show_url_name, args=(model.id,))
        self.assertEqual(url, model.get_absolute_url()) #get_absolute_url referance show page

    def test_only_models_in_submitted_and_acceped_states_listed_in_progress_tab(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertIn(model.state, [SUBMITTED,ACCEPTED])

    def test_models_in_company_field_match_company_in_user_session_in_progress_tab(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.company,self.user.pro_company.company)

    def test_only_models_in_approved_states_listed_in_approved_tab(self):
        url = reverse(self.list_url_name,args=(2,))
        self.response = self.client.get(url)

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.state, APPROVED)

    def test_models_in_company_field_match_company_in_user_session_in_approved_tab(self):
        url = reverse(self.list_url_name,args=(2,))
        self.response = self.client.get(url)

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.company,self.user.pro_company.company)

    def test_only_models_in_rejected_states_listed_in_rejected_tab(self):
        url = reverse(self.list_url_name,args=(3,))
        self.response = self.client.get(url)
        # print(help(self.client.request))

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.state, REJECTED)

    def test_models_in_company_field_match_company_in_user_session_in_rejected_tab(self):
        url = reverse(self.list_url_name,args=(3,))
        self.response = self.client.get(url)
        # print(help(self.client.request))

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.company,self.user.pro_company.company)

    def test_resolves_view_from_url(self):
        request = RequestFactory().get(self.list_url_path)
        request.user = self.user

        view = self.list_view_class()
        view.setup(request)
        view.dispatch(request)

        lst = view.get_queryset().all()
        for model in lst:
            self.assertIn(model.state, [SUBMITTED,ACCEPTED])

    def test_post_valid_data_to_create_new_app_page_not_raise_errors(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)
        
        self.assertNotContains(self.response, 'has-error') #form show errors

        for k in attachments.keys():
            attachments[k].close()

    def test_posting_valid_data_to_create_new_app_page_add_new_record(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        old_count = self.add_model.objects.count()

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)
        new_count = self.add_model.objects.count()
        
        self.assertEqual(new_count, old_count+1) #new record added

        for k in attachments.keys():
            attachments[k].close()

    def test_view_add_after_inserting_new_record_send_an_email(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)
        
        self.assertEqual(len(mail.outbox), 1) #email sent

        for k in attachments.keys():
            attachments[k].close()

    def test_view_add_after_inserting_new_record_send_an_email_with_correct_subject(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)

        self.assertEqual(mail.outbox[0].subject, self.add_email_subject_contain) #correct email subject

        for k in attachments.keys():
            attachments[k].close()

    def test_view_add_after_inserting_new_record_send_an_email_with_correct_body(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)

        self.assertIn(self.add_email_body_contain, mail.outbox[0].body) #correct email body

        for k in attachments.keys():
            attachments[k].close()

    def test_view_list_not_accessable_after_logout(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.client.logout()

        self.response = self.client.get(url)
        self.assertNotEqual(self.response.status_code, 200)

    def test_view_add_not_accessable_after_logout_with_get_action(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.client.logout()

        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertNotEqual(self.response.status_code, 200)

    def test_view_add_not_accessable_after_logout_with_post_action(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.client.logout()

        url = reverse(self.add_url_name)
        self.response = self.client.post(url)
        self.assertNotEqual(self.response.status_code, 200)

    def test_view_show_not_accessable_after_logout(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.client.logout()

        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertNotEqual(self.response.status_code, 200)

