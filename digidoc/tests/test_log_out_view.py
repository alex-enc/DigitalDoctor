from django.test import TestCase
from digidoc.models import User
from django.urls import reverse

class LogoutViewTestCase(TestCase):
    fixtures = ['digidoc/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.get(username='johndoe@example.org')


    def test_logout_url(self):
        self.assertEqual(self.url, '/log_out/')

    def test_logout(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())

    def test_post_signs_out_user_and_redirect_to_home(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, reverse('home'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()