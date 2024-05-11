import io 

from django.conf import settings
from django.urls import reverse

from django.contrib.auth import get_user_model

from pa.models import STATE_TYPE_CONFIRM, STATE_TYPE_DRAFT

class CommonViewTests():
    fixtures = ['testdata.yaml']

    username = "admin"

    list_view_class = None 
    list_template_name = ''
    list_context_object_name = 'apps'
    list_url_name = ''

    add_view_class = None
    add_template_name = ''
    add_url_name = ''
    add_model = None
    add_data = {}
    add_file_data = []

    show_view_class = None
    show_template_name = ''
    show_url_name = ''

    update_view_class = None
    update_template_name = ''
    update_url_name = ''

    delete_view_class = None
    delete_template_name = ''
    delete_url_name = ''

    invalid_data = {}

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username=self.username)
        self.client.force_login(self.user,settings.AUTHENTICATION_BACKENDS[0])

    def test_list_status_code(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertEqual(self.response.status_code, 200)

    def test_list_view_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        self.assertIs(self.response.resolver_match.func.view_class, self.list_view_class)

    def test_list_template_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertTemplateUsed(self.response, self.list_template_name)

    def test_add_status_code(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_add_view_used(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertIs(self.response.resolver_match.func.view_class, self.list_view_class)

    def test_add_template_used(self):
        url = reverse(self.add_url_name)
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response, self.add_template_name)

    def test_add_post_valid_data_not_raise_errors(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)
        self.assertNotContains(self.response, 'has-error') 
        
        for k in attachments.keys():
            attachments[k].close()

    def test_add_post_invalid_data_raise_errors(self):
        attachments = {}
        data = self.invalid_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, 'has-error') #form show errors
        
        for k in attachments.keys():
            attachments[k].close()

    def test_add_post_valid_data_add_new_record(self):
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

    def test_add_post_valid_data_set_log_data(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)
        model = self.add_model.objects.last()
        
        self.assertTrue(model.created_at)
        self.assertTrue(model.updated_at)
        self.assertTrue(model.created_by)
        self.assertTrue(model.updated_by)

        for k in attachments.keys():
            attachments[k].close()

    def test_add_post_valid_data_add_new_record_as_draft(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        data['_save_draft'] = 'ok'
        data['_save_confirm'] = ''

        old_count_draft = self.add_model.objects.filter(state=STATE_TYPE_DRAFT).count()
        old_count_confirmed = self.add_model.objects.filter(state=STATE_TYPE_CONFIRM).count()

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)

        new_count_draft = self.add_model.objects.filter(state=STATE_TYPE_DRAFT).count()
        new_count_confirmed = self.add_model.objects.filter(state=STATE_TYPE_CONFIRM).count()

        self.assertEqual(new_count_draft, old_count_draft+1)
        self.assertEqual(new_count_confirmed, old_count_confirmed)

        for k in attachments.keys():
            attachments[k].close()

    def test_add_post_valid_data_add_new_record_as_confirmed(self):
        attachments = {}
        data = self.add_data
        for k in self.add_file_data:
            attachments[k] = io.StringIO("some data")
            data[k] = attachments[k]

        data['_save_draft'] = ''
        data['_save_confirm'] = 'ok'

        old_count_draft = self.add_model.objects.filter(state=STATE_TYPE_DRAFT).count()
        old_count_confirmed = self.add_model.objects.filter(state=STATE_TYPE_CONFIRM).count()

        url = reverse(self.add_url_name)
        self.response = self.client.post(url, data, follow=True)

        new_count_draft = self.add_model.objects.filter(state=STATE_TYPE_DRAFT).count()
        new_count_confirmed = self.add_model.objects.filter(state=STATE_TYPE_CONFIRM).count()
        
        self.assertEqual(new_count_draft, old_count_draft)
        self.assertEqual(new_count_confirmed, old_count_confirmed+1)

        for k in attachments.keys():
            attachments[k].close()

    def test_show_status_code(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertGreaterEqual(len(lst),1) #no data for test #no data for test
        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertEqual(self.response.status_code, 200)

    def test_show_view_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertGreaterEqual(len(lst),1) #no data for test #no data for test
        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertIs(self.response.resolver_match.func.view_class, self.show_view_class)

    def test_show_template_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertGreaterEqual(len(lst),1) #no data for test

        for model in lst:
            url = reverse(self.show_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertTemplateUsed(self.response, self.show_template_name)

    def test_update_status_code_draft_exists(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertGreaterEqual(len(lst),1) #no data for test #no data for test
        for model in lst.filter(state=STATE_TYPE_DRAFT):
            url = reverse(self.update_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertEqual(self.response.status_code, 200)

    def test_update_status_code_confirmed_not_exists(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]

        self.assertGreaterEqual(len(lst),1) #no data for test #no data for test

        for model in lst.filter(state=STATE_TYPE_CONFIRM):
            url = reverse(self.update_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertNotEqual(self.response.status_code, 200)

    def test_update_view_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertGreaterEqual(len(lst),1) #no data for test
        for model in lst.filter(state=STATE_TYPE_DRAFT):
            url = reverse(self.update_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertIs(self.response.resolver_match.func.view_class, self.update_view_class)

    def test_update_template_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertGreaterEqual(len(lst.filter(state=STATE_TYPE_DRAFT)),1) #no data for test

        for model in lst.filter(state=STATE_TYPE_DRAFT):
            url = reverse(self.update_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertTemplateUsed(self.response, self.update_template_name)

    def test_delete_status_code_draft_exists(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertGreaterEqual(len(lst),1) #no data for test
        for model in lst.filter(state=STATE_TYPE_DRAFT):
            url = reverse(self.delete_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertEqual(self.response.status_code, 200)

    def test_delete_status_code_confirmed_not_exists(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]

        self.assertGreaterEqual(len(lst),1) #no data for test

        for model in lst.filter(state=STATE_TYPE_CONFIRM):
            url = reverse(self.delete_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertNotEqual(self.response.status_code, 200)

    def test_delete_view_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertGreaterEqual(len(lst),1) #no data for test #no data for test
        for model in lst.filter(state=STATE_TYPE_DRAFT):
            url = reverse(self.delete_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertIs(self.response.resolver_match.func.view_class, self.delete_view_class)

    def test_delete_template_used(self):
        url = reverse(self.list_url_name)
        self.response = self.client.get(url)
        lst = self.response.context[self.list_context_object_name]
        self.assertGreaterEqual(len(lst.filter(state=STATE_TYPE_DRAFT)),1) #no data for test

        for model in lst.filter(state=STATE_TYPE_DRAFT):
            url = reverse(self.delete_url_name, args=(model.id,))
            self.response = self.client.get(url)
            self.assertTemplateUsed(self.response, self.delete_template_name)
