from django.test import TestCase
from digidoc.models.message_models import Message
from django.core.exceptions import ValidationError

# Create your tests here.
class MessagerModelTestCase(TestCase):
    #tests whether the user created is valid
    def setUp(self):
        self.message = Message(
            sender = "You",
            content="I have a headache."
        )

    def test_valid_message(self):
        try:
            self.message.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_sender_must_not_be_blank(self):
        self.message.sender = None
        with self.assertRaises(ValidationError):
            self.message.full_clean()

    def test_content_must_not_be_blank(self):
        self.message.content = ''
        with self.assertRaises(ValidationError):
            self.message.full_clean()


   