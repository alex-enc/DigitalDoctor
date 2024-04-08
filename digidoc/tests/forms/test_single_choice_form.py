from django.test import TestCase
from digidoc.models.symptom_checker_models import SingleChoice
from digidoc.forms.symptom_checker_forms import SingleChoiceForm

# tests for the SingleChoiceForm
class SingleChoiceFormTestCase(TestCase):
    def setUp(self):
        # Create some SingleChoice objects for testing
        SingleChoice.objects.create(label='Few hours', choice_id = 'hour', conversation_id = 'c93fef2b-f6bf-4cd8-b4c8-4cb3e605496e')
        SingleChoice.objects.create(label='Few days', choice_id = 'day', conversation_id = 'c93fef2b-f6bf-4cd8-b4c8-4cb3e605496e')
        SingleChoice.objects.create(label='Few weeks', choice_id = 'week', conversation_id = 'c93fef2b-f6bf-4cd8-b4c8-4cb3e605496e')
        SingleChoice.objects.create(label='Few months', choice_id = 'month', conversation_id = 'c93fef2b-f6bf-4cd8-b4c8-4cb3e605496e')
        SingleChoice.objects.create(label='More than 3 months', choice_id = 'year', conversation_id = 'c93fef2b-f6bf-4cd8-b4c8-4cb3e605496e')

    def test_valid_single_choice_form(self):
        input = {
            'choices': SingleChoice.objects.first().id  # Select the first option
        }
        form = SingleChoiceForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_single_choice_form(self):
        input = {}
        form = SingleChoiceForm(data=input)
        self.assertFalse(form.is_valid())