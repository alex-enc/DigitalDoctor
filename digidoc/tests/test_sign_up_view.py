from django.test import TestCase
from digidoc.forms import SignUpForm
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from digidoc.models import User


#sign up view tests
class SignUpViewTestCase(TestCase):
    def test_get_sign_up(self):
        url = reverse('sign_up')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))

    # def test_successful_sign_up(self):
    #     response = self.client.post(self.url, self.form_input, follow=True)
    #     response_url = reverse('chat')
    #     self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'chat.html')