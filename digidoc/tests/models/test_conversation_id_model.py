from django.test import TestCase
from digidoc.models.symptom_checker_models import ConversationId
from django.core.exceptions import ValidationError

# tests for the ConversationId model
class ConversationIdModelTestCase(TestCase):
    def setUp(self):
        self.conversation_id = ConversationId(
            conversation_id = "20a922e9-3104-45e9-a185-a8a7befaabb5"
        )
    
    def test_valid_conversation_id(self):
        try:
            self.conversation_id.full_clean()
        except ValidationError:
            self.fail("Test ConversationId model should be valid")

    def test_conversation_id_must_not_be_blank(self):
        self.conversation_id.conversation_id = None
        with self.assertRaises(ValidationError):
            self.conversation_id.full_clean()