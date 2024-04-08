from django.test import TestCase
from digidoc.models.symptom_checker_models import MultipleChoice
from django.core.exceptions import ValidationError

# tests for MultipleChoice Model
class MultipleChoiceModelTestCase(TestCase):
    def setUp(self):
        self.multiple_choice = MultipleChoice(
            name = "Diabetes",
            choice_id = "C0011849",
            conversation_id = "20a922e9-3104-45e9-a185-a8a7befaabb5",
        )
    
    def test_valid_multiple_choice(self):
        try:
            self.multiple_choice.full_clean()
        except ValidationError:
            self.fail("Test MultipleChoice model should be valid")

    def test_name_must_not_be_blank(self):
        self.multiple_choice.name = None
        with self.assertRaises(ValidationError):
            self.multiple_choice.full_clean()

    def test_choice_id_must_not_be_blank(self):
        self.multiple_choice.choice_id = None
        with self.assertRaises(ValidationError):
            self.multiple_choice.full_clean()

    def test_conversation_id_must_not_be_blank(self):
        self.multiple_choice.conversation_id = None
        with self.assertRaises(ValidationError):
            self.multiple_choice.full_clean()