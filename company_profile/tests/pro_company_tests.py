import io 

from django.test import RequestFactory
from django.urls import reverse, resolve
from django.conf import settings

from django.core import mail
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model

from ..workflow import get_sumitted_responsible,SUBMITTED,ACCEPTED,APPROVED,REJECTED

class ProCompanyTests():
    fixtures = ['test_data.yaml']

    username = ""

    list_view_class = None 
    list_template_name = ''
    list_context_object_name = ''
    list_url_name = ''
    list_url_path = ''
    list_html_contain_ar = []
    list_html_contain_en = []

    show_view_class = None
    show_template_name = ''
    show_url_name = ''
    show_url_path = ''
    show_html_contain_ar = []
    show_html_contain_en = []

    add_template_name = ''
    add_url_name = ''
    add_url_path = ''
    add_html_contain_ar = []
    add_html_contain_en = []

    add_model = None
    add_data = {}
    add_file_data = []

    add_email_to = '' #assign in setUp func
    add_email_subject_contain_ar = ['']
    add_email_subject_contain_en = ['']
    add_email_body_template_ar = ''
    add_email_body_template_en = ''

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username=self.username)
        self.client.force_login(self.user,settings.AUTHENTICATION_BACKENDS[0])

        self.add_email_to = get_sumitted_responsible('pro_company').email

    def set_lang(self,lang):
        self.user.lang = lang
        self.user.save()
        self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: lang})

    def test_view_list_status_code(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertEqual(self.response.status_code, 200)

    def test_view_add_status_code(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_view_show_status_code(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]

        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertEqual(self.response.status_code, 200)

    def test_view_list_template_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertTemplateUsed(self.response, self.list_template_name)

    def test_view_add_template_used(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, self.add_template_name)

    def test_view_show_template_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]

        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertTemplateUsed(self.response, self.show_template_name)

    def test_view_list_contain_array_of_text_en(self):
        self.set_lang('en')
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        for c in self.list_html_contain_en:
            self.assertContains(self.response, c)

    def test_view_list_contain_array_of_text_ar(self):
        self.set_lang('ar')
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        for c in self.list_html_contain_ar:
            self.assertContains(self.response, c)


    def test_view_add_contain_array_of_text_ar(self):
        self.set_lang('ar')
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        for c in self.add_html_contain_ar:
            self.assertContains(self.response, c)

    def test_view_add_contain_array_of_text_en(self):
        self.set_lang('en')
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        for c in self.add_html_contain_en:
            self.assertContains(self.response, c)

    def test_view_show_contain_array_of_text_ar(self):
        self.set_lang('ar')
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]

        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)     
            for c in self.show_html_contain_ar:       
                self.assertContains(self.response, c)

    def test_view_show_contain_array_of_text_en(self):
        self.set_lang('en')
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]

        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)     
            for c in self.show_html_contain_en:       
                self.assertContains(self.response, c)

    def test_model_has_get_absolute_url_func(self):
        model = self.add_model.objects.first()
        self.assertTrue(hasattr(model,'get_absolute_url')) #model implement get_absolute_url

    def test_model_get_absolute_url_return_correct_url(self):
        model = self.add_model.objects.first()
        url = reverse(self.show_url_name, args=(model.id,))
        self.assertEqual(url, model.get_absolute_url()) #get_absolute_url referance show page

    def test_view_list_only_submitted_and_acceped_states_listed_in_progress_tab(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertIn(model.state, [SUBMITTED,ACCEPTED])

    def test_view_list_company_field_match_company_in_user_session_in_progress_tab(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.company,self.user.pro_company.company)

    def test_view_list_only_approved_states_listed_in_approved_tab(self):
        url = reverse(self.list_url_name,args=(2,))
        self.response = self.client.get(url)

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.state, APPROVED)

    def test_view_list_company_field_match_company_in_user_session_in_approved_tab(self):
        url = reverse(self.list_url_name,args=(2,))
        self.response = self.client.get(url)

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.company,self.user.pro_company.company)

    def test_view_list_only_rejected_states_listed_in_rejected_tab(self):
        url = reverse(self.list_url_name,args=(3,))
        self.response = self.client.get(url)
        # print(help(self.client.request))

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.state, REJECTED)

    def test_view_list_company_field_match_company_in_user_session_in_rejected_tab(self):
        url = reverse(self.list_url_name,args=(3,))
        self.response = self.client.get(url)
        # print(help(self.client.request))

        lst = self.response.context[self.list_context_object_name]
        for model in lst:
            self.assertEqual(model.company,self.user.pro_company.company)

    def test_view_list_resolves_view_from_url_path(self):
        request = RequestFactory().get(self.list_url_path)
        request.user = self.user

        view = self.list_view_class()
        view.setup(request)
        view.dispatch(request)

        lst = view.get_queryset().all()
        for model in lst:
            self.assertIn(model.state, [SUBMITTED,ACCEPTED])

    def test_user_assigned_to_group_pro_company_application_accept(self):
        User = get_user_model()
        count = User.objects.filter(groups__name="pro_company_application_accept").count()
        self.assertGreaterEqual(count,1)

    def test_view_add_post_valid_data_not_raise_errors(self):
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

    def test_view_add_post_valid_data_add_new_record(self):
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

    def test_view_add_post_valid_data_send_email(self):
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

    def test_view_add_post_valid_data_send_email_to_correct_receiver(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)
        
        self.assertIn(self.add_email_to, mail.outbox[0].to) #email to

        for k in attachments.keys():
            attachments[k].close()

    def test_view_add_post_valid_data_send_email_with_correct_subject_ar(self):
        self.set_lang('ar')
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)

        for c in self.add_email_subject_contain_ar:
            self.assertEqual(mail.outbox[0].subject, c) #correct email subject

        for k in attachments.keys():
            attachments[k].close()

    def test_view_add_post_valid_data_send_email_with_correct_subject_en(self):
        self.set_lang('en')
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)

        for c in self.add_email_subject_contain_en:
            self.assertEqual(mail.outbox[0].subject, c) #correct email subject

        for k in attachments.keys():
            attachments[k].close()

    def test_view_add_post_valid_data_send_email_with_correct_body_ar(self):
        self.set_lang('ar')
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)

        change_model = self.add_model.objects.last()
        info = (change_model._meta.app_label, change_model._meta.model_name)
        admin_url = settings.BASE_URL+reverse('admin:%s_%s_change' % info, args=(change_model.id,))
        messsage = render_to_string(self.add_email_body_template_ar,{'url':admin_url})

        self.assertEqual(messsage, mail.outbox[0].body) #correct email body

        for k in attachments.keys():
            attachments[k].close()

    def test_view_add_post_valid_data_send_email_with_correct_body_en(self):
        self.set_lang('en')
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)

        change_model = self.add_model.objects.last()
        info = (change_model._meta.app_label, change_model._meta.model_name)
        admin_url = settings.BASE_URL+reverse('admin:%s_%s_change' % info, args=(change_model.id,))
        messsage = render_to_string(self.add_email_body_template_en,{'url':admin_url})

        self.assertEqual(messsage, mail.outbox[0].body) #correct email body

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

