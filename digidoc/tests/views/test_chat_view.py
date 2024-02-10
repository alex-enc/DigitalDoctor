"""Tests of the feed view."""
from django.test import TestCase
from django.urls import reverse
from digidoc.forms.chat_forms import SendMessageForm
from digidoc.models.user_models import User


class ChatViewTestCase(TestCase):
    """Tests of the chat view."""

    def setUp(self):
        self.url = reverse('chat')

    def test_chat_url(self):
        self.assertEqual(self.url,'/chat/')

    def test_successful_message_sent(self):
        form_input = {'sender': 'You', 'content': 'I have a cough and a runny nose.', 'timestamp': '2018-11-20T15:58:44.767594-06:00'}
        response = self.client.post(self.url, form_input, follow=True)
        response_url = reverse('chat')
        # self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'chat.html')
    # def test_get_chat(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'chat.html')
    #     form = response.context['form']
    #     self.assertTrue(isinstance(form, MessageForm))
    #     self.assertFalse(form.is_bound)
