from django.test import TestCase
from digidoc.models.symptom_checker_models import MultipleChoice
from digidoc.forms.symptom_checker_forms import MultipleChoiceForm

# tests for the MultipleChoiceForm
class MultipleChoiceFormTestCase(TestCase):
    def setUp(self):
        # Create some MultipleChoice objects for testing
        MultipleChoice.objects.create(name='Cough', choice_id = 'assessment_C0010200', conversation_id = '9925155b-b473-4fdb-9611-51eeb1962346')
        MultipleChoice.objects.create(name='Runny node or nasal discharge', choice_id='assessment_C1260880', conversation_id = '9925155b-b473-4fdb-9611-51eeb1962346')
        MultipleChoice.objects.create(name='Throat irritation', choice_id = 'clarify_C0700184', conversation_id = '9925155b-b473-4fdb-9611-51eeb1962346')

    def test_valid_multiple_choice_form(self):
        input = {
            'multiple_choices': MultipleChoice.objects.values_list('id', flat=True)
        }
        form = MultipleChoiceForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_multiple_choice_form(self):
        input = {}
        form = MultipleChoiceForm(data=input)
        self.assertFalse(form.is_valid())