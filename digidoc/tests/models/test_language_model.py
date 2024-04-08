from django.test import TestCase
from digidoc.models.symptom_checker_models import Language
from django.core.exceptions import ValidationError

# tests for the Language model
class LanguageModelTestCase(TestCase):
    def setUp(self):
        self.language = Language(
            language = "English",
            language_code = "en"
        )
    
    def test_valid_language(self):
        try:
            self.language.full_clean()
        except ValidationError:
            self.fail("Test Language model should be valid")

    def test_language_must_not_be_blank(self):
        self.language.language = None
        with self.assertRaises(ValidationError):
            self.language.full_clean()

    def test_language_code_must_not_be_blank(self):
        self.language.language_code = None
        with self.assertRaises(ValidationError):
            self.language.full_clean()


   

   