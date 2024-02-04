"""Tests of the feed view."""
from django.test import TestCase
from django.urls import reverse
from digidoc.forms import SendMessageForm
from digidoc.models.user_models import User


class ChatViewTestCase(TestCase):
    """Tests of the chat view."""

    def setUp(self):
        self.url = reverse('chat')

    def test_chat_url(self):
        self.assertEqual(self.url,'/chat/')

    # def test_get_chat(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'chat.html')
    #     form = response.context['form']
    #     self.assertTrue(isinstance(form, MessageForm))
    #     self.assertFalse(form.is_bound)
