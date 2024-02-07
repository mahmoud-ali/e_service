from django.test import TestCase
from django.urls import reverse, resolve
from django.conf import settings

from django.contrib.auth import get_user_model

from ..views import HomePageView

class HomePageTests(TestCase):
    language = "en"
    username = "admin"

    view_class = HomePageView
    template_name = 'company_profile/home.html'
    url_name = 'profile:home'
    url_path = '/'
    html_contain = 'Home page here.'

    fixtures = ['test_data.yaml']

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username=self.username)

        self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: self.language})

        self.client.force_login(self.user,settings.AUTHENTICATION_BACKENDS[0])

        url = reverse(self.url_name)
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template(self):
        self.assertTemplateUsed(self.response, self.template_name)

    def test_contains_correct_html(self):
        self.assertContains(self.response, self.html_contain)

    def test_url_resolves_view(self): 
        view = resolve(self.url_path)
        self.assertEqual(
            view.func.__name__,
            self.view_class.as_view().__name__
        )

    def test_not_accessable_after_logout(self):
        self.client.logout()
        url = reverse(self.url_name)
        self.response = self.client.get(url)
        self.assertNotEqual(self.response.status_code, 200)


