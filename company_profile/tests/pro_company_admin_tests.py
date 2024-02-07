from django.urls import reverse
from django.conf import settings

from django.core import mail

from django.contrib.auth import get_user_model

from ..workflow import SUBMITTED,ACCEPTED,APPROVED,REJECTED

class ProCompanyAdminTests():
    fixtures = ['test_data.yaml']

    language = ""
    username = ""

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

    def test_admin_workflow_transition_from_submitted_to_accepted_not_raise_errors(self):
        qs = self.add_model.objects.filter(state=SUBMITTED)
        data = self.add_data
        data['state'] = ACCEPTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.add_model.__module__.split('.')[0].lower()+"_"+self.add_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertNotContains(self.response, 'errorlist') #form show errors

    def test_admin_workflow_transition_from_submitted_to_accepted_send_email(self):
        qs = self.add_model.objects.filter(state=SUBMITTED)
        data = self.add_data
        data['state'] = ACCEPTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.add_model.__module__.split('.')[0].lower()+"_"+self.add_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertEqual(len(mail.outbox), 1) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_approved_not_raise_errors(self):
        qs = self.add_model.objects.filter(state=ACCEPTED)
        data = self.add_data
        data['state'] = APPROVED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.add_model.__module__.split('.')[0].lower()+"_"+self.add_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertNotContains(self.response, 'errorlist') #form show errors

    def test_admin_workflow_transition_from_accepted_to_approved_send_email(self):
        qs = self.add_model.objects.filter(state=ACCEPTED)
        data = self.add_data
        data['state'] = APPROVED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.add_model.__module__.split('.')[0].lower()+"_"+self.add_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertEqual(len(mail.outbox), 1) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_rejected_not_raise_errors(self):
        qs = self.add_model.objects.filter(state=ACCEPTED)
        data = self.add_data
        data['state'] = REJECTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.add_model.__module__.split('.')[0].lower()+"_"+self.add_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertNotContains(self.response, 'errorlist') #form show errors

    def test_admin_workflow_transition_from_accepted_to_rejected_send_email(self):
        qs = self.add_model.objects.filter(state=ACCEPTED)
        data = self.add_data
        data['state'] = REJECTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.add_model.__module__.split('.')[0].lower()+"_"+self.add_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertEqual(len(mail.outbox), 1) #email sent
            mail.outbox = []

    def test_admin_workflow_invalid_transition_show_errors(self):
        qs = self.add_model.objects.filter(state=SUBMITTED)
        data = self.add_data
        for state in [APPROVED,REJECTED]:
            data['state'] = state

            for model in qs:
                data['company'] = model.company.id
                #url = admin:app_name_model_name_change
                url = reverse("admin:"+self.add_model.__module__.split('.')[0].lower()+"_"+self.add_model.__name__.lower()+"_change",args=(model.id,))
                self.response = self.client.post(url, data, follow=True) 
                self.assertContains(self.response, 'errorlist') #form show errors

    def test_admin_workflow_invalid_transition_not_send_email(self):
        qs = self.add_model.objects.filter(state=SUBMITTED)
        data = self.add_data
        for state in [APPROVED,REJECTED]:
            data['state'] = state

            for model in qs:
                data['company'] = model.company.id
                #url = admin:app_name_model_name_change
                url = reverse("admin:"+self.add_model.__module__.split('.')[0].lower()+"_"+self.add_model.__name__.lower()+"_change",args=(model.id,))
                self.response = self.client.post(url, data, follow=True) 
                self.assertEqual(len(mail.outbox), 0) #email sent


