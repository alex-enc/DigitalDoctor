from django.test import TestCase
from django.urls import reverse
from digidoc.models import User


class LoginViewTestCase(TestCase):
    fixtures = ['digidoc/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.get(username='johndoe@example.org')

    def test_view_url(self):
        self.assertEqual(self.url, '/log_in/')

    # def test_authenticated_user_redirected_to_home(self):
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.assertTrue(self._is_logged_in())
    #     response = self.client.get(self.url, follow=True)
    #     self.assertRedirects(response, reverse('chat'), status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'chat.html')

    def test_unauthenticated_user_renders_login(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

    # def test_successful_login(self):
    #     form_input = {'username': 'johndoe@example.com', 'password': 'Password123'}
    #     response = self.client.post(self.url, data=form_input, follow=True)
    #     self.assertRedirects(response, reverse('chat'), status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'chat.html')
    #     self.assertEqual(len(list(response.context['messages'])), 0)

    def test_login_with_incorrect_password(self):
        form_input = {'username': 'johndoe@example.com', 'password': 'Wr0ngP@ssword'}
        response = self.client.post(self.url, data=form_input, follow = True)
        self.assertFalse(self._is_logged_in())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assertNotEqual(len(list(response.context['messages'])), 0)

    def test_login_with_incorrect_email_format(self):
        form_input = {'username': 'johndoe.example.com', 'password': 'Password123'}
        response = self.client.post(self.url, data=form_input, follow=True)
        self.assertFalse(self._is_logged_in())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assertNotEqual(len(list(response.context['messages'])), 0)

    def test_login_with_blank_password(self):
        form_input = {'username':'johndoe@example.com', 'password':''}
        response = self.client.post(self.url, data=form_input, follow = True)
        self.assertFalse(self._is_logged_in())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assertNotEqual(len(list(response.context['messages'])), 0)

    def test_login_with_blank_username(self):
        form_input = {'username':'', 'password':'Password123'}
        response = self.client.post(self.url, data=form_input, follow=True)
        self.assertFalse(self._is_logged_in())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assertNotEqual(len(list(response.context['messages'])), 0)

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()