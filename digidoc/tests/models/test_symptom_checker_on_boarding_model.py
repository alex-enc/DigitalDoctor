from django.test import TestCase
from digidoc.models.symptom_checker_models import OnBoarding
from django.core.exceptions import ValidationError

# Create your tests here.

# tests for the OnBoarding model
class OnBoardingModelTestCase(TestCase):
    def setUp(self):
        self.on_boarding = OnBoarding(
            name = "John Doe",
            gender = "Male",
            birth_year = "1990",
            initial_symptoms = 'Runny nose, headache, cough'
        )
    
    def test_valid_on_boarding(self):
        try:
            self.on_boarding.full_clean()
        except ValidationError:
            self.fail("Test OnBoarding model should be valid")

    def test_name_must_not_be_blank(self):
        self.on_boarding.name = None
        with self.assertRaises(ValidationError):
            self.on_boarding.full_clean()

    def test_gender_must_not_be_blank(self):
        self.on_boarding.gender = None
        with self.assertRaises(ValidationError):
            self.on_boarding.full_clean()

    def test_birth_year_must_not_be_blank(self):
        self.on_boarding.birth_year = None
        with self.assertRaises(ValidationError):
            self.on_boarding.full_clean()

    def test_initial_symptoms_must_not_be_blank(self):
        self.on_boarding.initial_symptoms = None
        with self.assertRaises(ValidationError):
            self.on_boarding.full_clean()