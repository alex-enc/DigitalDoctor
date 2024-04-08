from django.test import TestCase
from digidoc.models.symptom_checker_models import TextInput
from django.core.exceptions import ValidationError

# tests for the TextInput model
class TextInputModelTestCase(TestCase):
    def setUp(self):
        self.text_input = TextInput(
            symptom_name = "Cough"
        )
    
    def test_valid_text_input(self):
        try:
            self.text_input.full_clean()
        except ValidationError:
            self.fail("Test TextInput model should be valid")

    def test_phase_must_not_be_blank(self):
        self.text_input.symptom_name = None
        with self.assertRaises(ValidationError):
            self.text_input.full_clean()