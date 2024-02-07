from django.test import TestCase
from django.urls import reverse, resolve
from django.conf import settings
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model

from ..views import LkpLocalitySelectView
from ..models import LkpState, LkpLocality

class HomePageTests(TestCase):
    username = "admin"

    view_class = LkpLocalitySelectView
    model_class = LkpLocality
    master_class = LkpState
    template_name = 'company_profile/select.html'
    url_name = 'profile:lkp_locality_select'

    fixtures = ['test_data.yaml']

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username=self.username)

        self.client.force_login(self.user,settings.AUTHENTICATION_BACKENDS[0])

        self.master_id = self.master_class.objects.first().id
        model = self.model_class.objects.filter(state__id = self.master_id)

        self.url = reverse(self.url_name,args=(self.master_id,model.first().id))
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template(self):
        self.assertTemplateUsed(self.response, self.template_name)

    def test_template_render_correct_data(self):
        qs = self.model_class.objects.filter(state__id = self.master_id)
#        temp = render_to_string(self.template_name,{'options':qs,'old_value':qs.first().id})
#        print('1:',temp)
#        print('1:',self.response.context['options'])
        self.assertEqual(list(self.response.context['options']), list(qs))

    def test_not_accessable_after_logout(self):
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertNotEqual(self.response.status_code, 200)


