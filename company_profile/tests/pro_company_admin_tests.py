from django.urls import reverse
from django.conf import settings

from django.core import mail
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from ..workflow import SUBMITTED,ACCEPTED,APPROVED,REJECTED

class ProCompanyAdminTests():
    fixtures = ['test_data.yaml']

    username = ""

    admin_accepted_email_to = '' #assign in setUp func
    admin_accepted_email_subject_contain_ar = ['']
    admin_accepted_email_subject_contain_en = ['']
    admin_approved_email_to = '' #assign in setUp func
    admin_approved_email_subject_contain_ar = ['']
    admin_approved_email_subject_contain_en = ['']
    admin_rejected_email_to = '' #assign in setUp func
    admin_rejected_email_subject_contain_ar = ['']
    admin_rejected_email_subject_contain_en = ['']

    admin_accepted_email_body_template_ar = ''
    admin_accepted_email_body_template_en = ''
    admin_approved_email_body_template_ar = ''
    admin_approved_email_body_template_en = ''
    admin_rejected_email_body_template_ar = ''
    admin_rejected_email_body_template_en = ''

    change_model = None
    change_data = {}

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username=self.username)
        self.admin_accepted_email_to = self.admin_approved_email_to = self.admin_rejected_email_to = self.user.pro_company.company.email

        self.client.force_login(self.user,settings.AUTHENTICATION_BACKENDS[0])

    def set_lang(self,lang):
        self.user.lang = lang
        self.user.save()
        self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: lang})

    def test_user_assigned_to_group_pro_company_application_approve(self):
        User = get_user_model()
        count = User.objects.filter(groups__name="pro_company_application_approve").count()
        self.assertGreaterEqual(count,1)

    def test_admin_workflow_transition_from_submitted_to_accepted_not_raise_errors(self):
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertNotContains(self.response, 'errorlist') #form show errors

    def test_admin_workflow_transition_from_submitted_to_accepted_send_email(self):
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertEqual(len(mail.outbox), 1) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_submitted_to_accepted_send_email_to_correct_receiver(self):
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertIn(self.admin_accepted_email_to, mail.outbox[0].to) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_submitted_to_accepted_send_email_with_correct_subject_ar(self):
        self.set_lang('ar')
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            for c in self.admin_accepted_email_subject_contain_ar:
                self.assertEqual(mail.outbox[0].subject, c) #correct email subject
            mail.outbox = []

    def test_admin_workflow_transition_from_submitted_to_accepted_send_email_with_correct_subject_en(self):
        self.set_lang('en')
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            for c in self.admin_accepted_email_subject_contain_en:
                self.assertEqual(mail.outbox[0].subject, c) #correct email subject
            mail.outbox = []

    def test_admin_workflow_transition_from_submitted_to_accepted_send_email_with_correct_body_ar(self):
        self.set_lang('ar')
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 

            email_url = 'https://'+Site.objects.get_current().domain+model.get_absolute_url()
            messsage = render_to_string(self.admin_accepted_email_body_template_ar,{'url':email_url})

            self.assertEqual(messsage, mail.outbox[0].body) #correct email body
            mail.outbox = []

    def test_admin_workflow_transition_from_submitted_to_accepted_send_email_with_correct_body_en(self):
        self.set_lang('en')
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 

            email_url = 'https://'+Site.objects.get_current().domain+model.get_absolute_url()
            messsage = render_to_string(self.admin_accepted_email_body_template_en,{'url':email_url})

            self.assertEqual(messsage, mail.outbox[0].body) #correct email body
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_approved_not_raise_errors(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = APPROVED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertNotContains(self.response, 'errorlist') #form show errors

    def test_admin_workflow_transition_from_accepted_to_approved_send_email(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = APPROVED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertEqual(len(mail.outbox), 1) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_approved_send_email_to_correct_receiver(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = APPROVED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertIn(self.admin_approved_email_to, mail.outbox[0].to) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_approved_send_email_with_correct_subject_ar(self):
        self.set_lang('ar')
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = APPROVED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            for c in self.admin_approved_email_subject_contain_ar:
                self.assertEqual(mail.outbox[0].subject, c) #correct email subject
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_approved_send_email_with_correct_subject_en(self):
        self.set_lang('en')
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = APPROVED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            for c in self.admin_approved_email_subject_contain_en:
                self.assertEqual(mail.outbox[0].subject, c) #correct email subject
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_approved_send_email_with_correct_body_ar(self):
        self.set_lang('ar')
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = APPROVED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 

            email_url = 'https://'+Site.objects.get_current().domain+model.get_absolute_url()
            messsage = render_to_string(self.admin_approved_email_body_template_ar,{'url':email_url})

            self.assertEqual(messsage, mail.outbox[0].body) #correct email body
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_approved_send_email_with_correct_body_en(self):
        self.set_lang('en')
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = APPROVED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 

            email_url = 'https://'+Site.objects.get_current().domain+model.get_absolute_url()
            messsage = render_to_string(self.admin_approved_email_body_template_en,{'url':email_url})

            self.assertEqual(messsage, mail.outbox[0].body) #correct email body
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_rejected_not_raise_errors(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertNotContains(self.response, 'errorlist') #form show errors

    def test_admin_workflow_transition_from_accepted_to_rejected_send_email(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertEqual(len(mail.outbox), 1) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_rejected_send_email_correct_receiver(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            self.assertIn(self.admin_rejected_email_to, mail.outbox[0].to) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_rejected_send_email_with_correct_subject_ar(self):
        self.set_lang('ar')
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            for c in self.admin_rejected_email_subject_contain_ar:
                self.assertEqual(mail.outbox[0].subject, c) #correct email subject
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_rejected_send_email_with_correct_subject_en(self):
        self.set_lang('en')
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            for c in self.admin_rejected_email_subject_contain_en:
                self.assertEqual(mail.outbox[0].subject, c) #correct email subject
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_rejected_send_email_with_correct_body_ar(self):
        self.set_lang('ar')
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 

            email_url = 'https://'+Site.objects.get_current().domain+model.get_absolute_url()
            messsage = render_to_string(self.admin_rejected_email_body_template_ar,{'url':email_url})

            self.assertEqual(messsage, mail.outbox[0].body) #correct email body
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_rejected_send_email_with_correct_body_en(self):
        self.set_lang('en')
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED

        for model in qs:
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 

            email_url = 'https://'+Site.objects.get_current().domain+model.get_absolute_url()
            messsage = render_to_string(self.admin_rejected_email_body_template_en,{'url':email_url})

            self.assertEqual(messsage, mail.outbox[0].body) #correct email body
            mail.outbox = []

    def test_admin_workflow_invalid_transition_show_errors(self):
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        for state in [APPROVED,REJECTED]:
            data['state'] = state

            for model in qs:
                data['company'] = model.company.id
                #url = admin:app_name_model_name_change
                url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
                self.response = self.client.post(url, data, follow=True) 
                self.assertContains(self.response, 'errorlist') #form show errors

    def test_admin_workflow_invalid_transition_not_send_email(self):
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        for state in [APPROVED,REJECTED]:
            data['state'] = state

            for model in qs:
                data['company'] = model.company.id
                #url = admin:app_name_model_name_change
                url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
                self.response = self.client.post(url, data, follow=True) 
                self.assertEqual(len(mail.outbox), 0) #email sent


