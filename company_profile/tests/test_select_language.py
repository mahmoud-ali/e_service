from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from django.contrib.auth import get_user_model

#from ..views import SetLanguageView

class HomePageTests(TestCase):
    language = "en"
    username = "admin"

    #view_class = SetLanguageView
    url_name = 'profile:set_lang'
    url_path = '/set_lang'

    fixtures = ['test_data.yaml']

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username=self.username)

        self.client.force_login(self.user,settings.AUTHENTICATION_BACKENDS[0])

    def test_language_changed_to_arabic(self):
        url = reverse(self.url_name)
        self.response = self.client.post(url,{'language':'ar'})

        User = get_user_model()
        self.user = User.objects.get(username=self.username)

        self.assertEqual(self.user.lang, 'ar')

    def test_language_changed_to_english(self):
        url = reverse(self.url_name)
        self.response = self.client.post(url,{'language':'en'})

        User = get_user_model()
        self.user = User.objects.get(username=self.username)

        self.assertEqual(self.user.lang, 'en')

    def test_not_accessable_after_logout(self):
        self.client.logout()
        url = reverse(self.url_name)
        self.response = self.client.get(url)
        self.assertNotEqual(self.response.status_code, 200)


