from django.test import TestCase
from digidoc.models.symptom_checker_models import SingleChoice
from django.core.exceptions import ValidationError

# tests for the SingleChoice model
class SingleChoiceModelTestCase(TestCase):
    def setUp(self):
        self.single_choice = SingleChoice(
            label = "Few hours",
            choice_id = "hour",
            conversation_id = "20a922e9-3104-45e9-a185-a8a7befaabb5"
        )
    
    def test_valid_single_choice(self):
        try:
            self.single_choice.full_clean()
        except ValidationError:
            self.fail("Test SingleChoice model should be valid")

    def test_label_must_not_be_blank(self):
        self.single_choice.label = None
        with self.assertRaises(ValidationError):
            self.single_choice.full_clean()

    def test_choice_id_must_not_be_blank(self):
        self.single_choice.choice_id = None
        with self.assertRaises(ValidationError):
            self.single_choice.full_clean()

    def test_conversation_id_must_not_be_blank(self):
        self.single_choice.conversation_id = None
        with self.assertRaises(ValidationError):
            self.single_choice.full_clean()