from django.test import TestCase
from digidoc.models.symptom_checker_models import OnBoarding
from digidoc.forms.symptom_checker_forms import OnBoardingForm

# tests for the OnBoardingForm
class OnBoardingFormTestCase(TestCase):
    def setUp(self):
        self.name = "John Doe"
        self.birth_year = 2000
        self.initial_symptoms = "Cough, sore throat, runny nose"

    def test_valid_on_boarding_form(self):
        input = {
                'name': self.name, 
                'birth_year': self.birth_year, 
                'initial_symptoms': self.initial_symptoms
                }
        form = OnBoardingForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_on_boarding_no_name_form(self):
        input = {
                'name': '',               
                'birth_year': self.birth_year, 
                'initial_symptoms': self.initial_symptoms
                }
        form = OnBoardingForm(data=input)
        self.assertFalse(form.is_valid())

    def test_invalid_on_boarding_no_birth_year_form(self):
        input = {
                'name': self.name,
                'birth_year': None, 
                'initial_symptoms': self.initial_symptoms
                } 
        form = OnBoardingForm(data=input)
        self.assertFalse(form.is_valid())

    def test_invalid_on_boarding_no_initial_symptoms_form(self):
        input = {
                'name': self.name,               
                'birth_year': self.birth_year, 
                'initial_symptoms': ''
                }
        form = OnBoardingForm(data=input)
        self.assertFalse(form.is_valid())

    def test_on_boarding_form_has_necessary_fields(self):
        form = OnBoardingForm()
        self.assertIn('name', form.fields)
        self.assertIn('birth_year', form.fields)
        self.assertIn('initial_symptoms', form.fields)

    def test_on_boarding_is_created(self):
        input = {
                'name': self.name, 
                'birth_year': self.birth_year, 
                'initial_symptoms': self.initial_symptoms
                }
        form = OnBoardingForm(data=input)
        count_before = OnBoarding.objects.count()
        form.save()
        count_after = OnBoarding.objects.count()
        self.assertEqual(count_after, count_before+1)