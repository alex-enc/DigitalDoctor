from django.test import TestCase
from digidoc.models.symptom_checker_models import TextInput
from digidoc.forms.symptom_checker_forms import TextInputForm

# tests for the TextInputForm
class TextInputFormTestCase(TestCase):
    def setUp(self):
        self.symptom_name = "Cough"

    def test_valid_on_boarding_form(self):
        input = {
                'symptom_name': self.symptom_name
                }
        form = TextInputForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_text_input_no_name_form(self):
        input = {
                'symptom_name': ''
                }
        form = TextInputForm(data=input)
        self.assertFalse(form.is_valid())


    def test_text_input_form_has_necessary_fields(self):
        form = TextInputForm()
        self.assertIn('symptom_name', form.fields)

    def test_on_boarding_is_created(self):
        input = {
                'symptom_name': self.symptom_name, 
                }
        form = TextInputForm(data=input)
        count_before = TextInput.objects.count()
        form.save()
        count_after = TextInput.objects.count()
        self.assertEqual(count_after, count_before+1)