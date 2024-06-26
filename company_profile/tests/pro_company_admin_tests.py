from django.urls import reverse
from django.conf import settings

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from ..workflow import SUBMITTED,ACCEPTED,APPROVED,REJECTED

class ProCompanyAdminTests():
    fixtures = ['test_data.yaml']

    username = "admin"

    admin_accepted_email_subject_contain_ar = ['تم استلام الطلب']
    admin_accepted_email_subject_contain_en = ['Application accepted']
    admin_approved_email_subject_contain_ar = ['تم تصديق الطلب']
    admin_approved_email_subject_contain_en = ['Application approved']
    admin_rejected_email_subject_contain_ar = ['تم رفض الطلب']
    admin_rejected_email_subject_contain_en = ['Application rejected']

    admin_accepted_email_body_template_ar = 'company_profile/email/accepted_email_ar.html'
    admin_accepted_email_body_template_en = 'company_profile/email/accepted_email_en.html'
    admin_approved_email_body_template_ar = 'company_profile/email/approved_email_ar.html'
    admin_approved_email_body_template_en = 'company_profile/email/approved_email_en.html'
    admin_rejected_email_body_template_ar = 'company_profile/email/rejected_email_ar.html'
    admin_rejected_email_body_template_en = 'company_profile/email/rejected_email_en.html'


    change_model = None
    change_data = {}

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username=self.username)
        self.admin_accepted_email_to = self.admin_approved_email_to = self.admin_rejected_email_to = self.user.pro_company.company.email

        self.client.force_login(self.user,settings.AUTHENTICATION_BACKENDS[0])

    def set_lang(self,lang,user=None):
        if user:
            user.lang = lang
            user.save()
        else:
            self.user.lang = lang
            self.user.save()

        self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: lang})

    def get_user(self,model):
        User = get_user_model()        
        user = User.objects.get(email=model.company.email)
        return user

    def test_user_assigned_to_group_pro_company_application_approve(self):
        User = get_user_model()
        count = User.objects.filter(groups__name="pro_company_application_approve").count()
        self.assertGreaterEqual(count,1)

    def test_admin_workflow_transition_from_submitted_to_accepted_not_raise_errors(self):
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            self.set_lang('en',user=self.get_user(model))
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
            self.assertIn(model.company.email, mail.outbox[0].to) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_submitted_to_accepted_send_email_with_correct_subject_ar(self):
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            self.set_lang('ar',user=self.get_user(model))
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            for c in self.admin_accepted_email_subject_contain_ar:
                self.assertEqual(mail.outbox[0].subject, c) #correct email subject
            mail.outbox = []

    # def test_admin_workflow_transition_from_submitted_to_accepted_send_email_with_correct_subject_en(self):
    #     qs = self.change_model.objects.filter(state=SUBMITTED)
    #     data = self.change_data
    #     data['state'] = ACCEPTED

    #     for model in qs:
    #         self.set_lang('en',user=self.get_user(model))
    #         data['company'] = model.company.id
    #         #url = admin:app_name_model_name_change
    #         url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
    #         self.response = self.client.post(url, data, follow=True) 
    #         for c in self.admin_accepted_email_subject_contain_en:
    #             self.assertEqual(mail.outbox[0].subject, c) #correct email subject
    #         mail.outbox = []

    def test_admin_workflow_transition_from_submitted_to_accepted_send_email_with_correct_body_ar(self):
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        data['state'] = ACCEPTED

        for model in qs:
            self.set_lang('ar',user=self.get_user(model))
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 

            email_url = 'https://'+Site.objects.get_current().domain+'/app'+model.get_absolute_url()
            messsage = render_to_string(self.admin_accepted_email_body_template_ar,{'url':email_url})

            self.assertEqual(strip_tags(messsage), mail.outbox[0].body) #correct email body
            mail.outbox = []

    # def test_admin_workflow_transition_from_submitted_to_accepted_send_email_with_correct_body_en(self):
    #     qs = self.change_model.objects.filter(state=SUBMITTED)
    #     data = self.change_data
    #     data['state'] = ACCEPTED

    #     for model in qs:
    #         self.set_lang('en',user=self.get_user(model))
    #         data['company'] = model.company.id
    #         #url = admin:app_name_model_name_change
    #         url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
    #         self.response = self.client.post(url, data, follow=True) 

    #         email_url = 'https://'+Site.objects.get_current().domain+model.get_absolute_url()
    #         messsage = render_to_string(self.admin_accepted_email_body_template_en,{'url':email_url})

    #         self.assertEqual(messsage, mail.outbox[0].body) #correct email body
    #         mail.outbox = []

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
            self.assertIn(self.get_user(model).email, mail.outbox[0].to) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_approved_send_email_with_correct_subject_ar(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = APPROVED

        for model in qs:
            self.set_lang('ar',user=self.get_user(model))
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            for c in self.admin_approved_email_subject_contain_ar:
                self.assertEqual(mail.outbox[0].subject, c) #correct email subject
            mail.outbox = []

    # def test_admin_workflow_transition_from_accepted_to_approved_send_email_with_correct_subject_en(self):
    #     qs = self.change_model.objects.filter(state=ACCEPTED)
    #     data = self.change_data
    #     data['state'] = APPROVED

    #     for model in qs:
    #         self.set_lang('en',user=self.get_user(model))
    #         data['company'] = model.company.id
    #         #url = admin:app_name_model_name_change
    #         url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
    #         self.response = self.client.post(url, data, follow=True) 
    #         for c in self.admin_approved_email_subject_contain_en:
    #             self.assertEqual(mail.outbox[0].subject, c) #correct email subject
    #         mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_approved_send_email_with_correct_body_ar(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = APPROVED

        for model in qs:
            self.set_lang('ar',user=self.get_user(model))
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 

            email_url = 'https://'+Site.objects.get_current().domain+'/app'+model.get_absolute_url()
            messsage = render_to_string(self.admin_approved_email_body_template_ar,{'url':email_url})

            self.assertEqual(strip_tags(messsage), mail.outbox[0].body) #correct email body
            mail.outbox = []

    # def test_admin_workflow_transition_from_accepted_to_approved_send_email_with_correct_body_en(self):
    #     qs = self.change_model.objects.filter(state=ACCEPTED)
    #     data = self.change_data
    #     data['state'] = APPROVED

    #     for model in qs:
    #         self.set_lang('en',user=self.get_user(model))
    #         data['company'] = model.company.id
    #         #url = admin:app_name_model_name_change
    #         url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
    #         self.response = self.client.post(url, data, follow=True) 

    #         email_url = 'https://'+Site.objects.get_current().domain+model.get_absolute_url()
    #         messsage = render_to_string(self.admin_approved_email_body_template_en,{'url':email_url})

    #         self.assertEqual(messsage, mail.outbox[0].body) #correct email body
    #         mail.outbox = []

    # def test_admin_workflow_transition_from_accepted_to_rejected_raise_errors(self):
    #     qs = self.change_model.objects.filter(state=ACCEPTED)
    #     data = self.change_data
    #     data['state'] = REJECTED

    #     for model in qs:
    #         self.set_lang('en',user=self.get_user(model))
    #         data['company'] = model.company.id
    #         #url = admin:app_name_model_name_change
    #         url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
    #         self.response = self.client.post(url, data, follow=True) 
    #         self.assertContains(self.response, 'errorlist') #form show errors

    def test_admin_workflow_transition_from_accepted_to_rejected_not_raise_errors(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED
        data['reject_comments'] = 'comment'

        for model in qs:
            self.set_lang('en',user=self.get_user(model))
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
#            print(self.response.content)
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
            self.assertIn(self.get_user(model).email, mail.outbox[0].to) #email sent
            mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_rejected_send_email_with_correct_subject_ar(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED

        for model in qs:
            self.set_lang('ar',user=self.get_user(model))
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 
            for c in self.admin_rejected_email_subject_contain_ar:
                self.assertEqual(mail.outbox[0].subject, c) #correct email subject
            mail.outbox = []

    # def test_admin_workflow_transition_from_accepted_to_rejected_send_email_with_correct_subject_en(self):
    #     qs = self.change_model.objects.filter(state=ACCEPTED)
    #     data = self.change_data
    #     data['state'] = REJECTED

    #     for model in qs:
    #         self.set_lang('en',user=self.get_user(model))
    #         data['company'] = model.company.id
    #         #url = admin:app_name_model_name_change
    #         url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
    #         self.response = self.client.post(url, data, follow=True) 
    #         for c in self.admin_rejected_email_subject_contain_en:
    #             self.assertEqual(mail.outbox[0].subject, c) #correct email subject
    #         mail.outbox = []

    def test_admin_workflow_transition_from_accepted_to_rejected_send_email_with_correct_body_ar(self):
        qs = self.change_model.objects.filter(state=ACCEPTED)
        data = self.change_data
        data['state'] = REJECTED

        for model in qs:
            self.set_lang('ar',user=self.get_user(model))
            data['company'] = model.company.id
            #url = admin:app_name_model_name_change
            url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
            self.response = self.client.post(url, data, follow=True) 

            email_url = 'https://'+Site.objects.get_current().domain+'/app'+model.get_absolute_url()
            messsage = render_to_string(self.admin_rejected_email_body_template_ar,{'url':email_url})

            self.assertEqual(strip_tags(messsage), mail.outbox[0].body) #correct email body
            mail.outbox = []

    # def test_admin_workflow_transition_from_accepted_to_rejected_send_email_with_correct_body_en(self):
    #     qs = self.change_model.objects.filter(state=ACCEPTED)
    #     data = self.change_data
    #     data['state'] = REJECTED

    #     for model in qs:
    #         self.set_lang('en',user=self.get_user(model))
    #         data['company'] = model.company.id
    #         #url = admin:app_name_model_name_change
    #         url = reverse("admin:"+self.change_model.__module__.split('.')[0].lower()+"_"+self.change_model.__name__.lower()+"_change",args=(model.id,))
    #         self.response = self.client.post(url, data, follow=True) 

    #         email_url = 'https://'+Site.objects.get_current().domain+model.get_absolute_url()
    #         messsage = render_to_string(self.admin_rejected_email_body_template_en,{'url':email_url})

    #         self.assertEqual(messsage, mail.outbox[0].body) #correct email body
    #         mail.outbox = []

    def test_admin_workflow_invalid_transition_show_errors(self):
        qs = self.change_model.objects.filter(state=SUBMITTED)
        data = self.change_data
        for state in [APPROVED,REJECTED]:
            data['state'] = state

            for model in qs:
                self.set_lang('en',user=self.get_user(model))
                
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


