from django.test import TestCase
from digidoc.models.symptom_checker_models import APIResponse
from django.core.exceptions import ValidationError

# tests for APIResponse model
class APIResponseModelTestCase(TestCase):
    def setUp(self):
        self.API_response = APIResponse(
            phase = "questions",
            question_type = "factor",
            choice_type = "single"
        )
    
    def test_valid_API_response(self):
        try:
            self.API_response.full_clean()
        except ValidationError:
            self.fail("Test APIResponse model should be valid")

    def test_phase_must_not_be_blank(self):
        self.API_response.phase = None
        with self.assertRaises(ValidationError):
            self.API_response.full_clean()

    def test_question_type_must_not_be_blank(self):
        self.API_response.question_type = None
        with self.assertRaises(ValidationError):
            self.API_response.full_clean()

    def test_choice_type_must_not_be_blank(self):
        self.API_response.choice_type = None
        with self.assertRaises(ValidationError):
            self.API_response.full_clean()