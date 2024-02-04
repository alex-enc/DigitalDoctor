from django.test import TestCase
from digidoc.models.message_models import Message
from digidoc.forms.chat_forms import SendMessageForm

class SendMessageFormTestCase(TestCase):
    def setUp(self):
        self.content = "I have a cough and a runny nose."

    def test_valid_message_form(self):
        input = {'content': self.content }
        form = SendMessageForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_invalid_form(self):
        input = {'content': '' }
        form = SendMessageForm(data=input)
        self.assertFalse(form.is_valid())