from django.test import TestCase
from digidoc.models.symptom_checker_models import OnBoarding, MultipleChoice, SingleChoice, APIResponse, TextInput, HealthBackground, ConversationId, Language
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

class HealthBackgroundModelTestCase(TestCase):
    def setUp(self):
        self.health_background = HealthBackground(
            condition_id = "C0004096"
        )
    
    def test_valid_health_background(self):
        try:
            self.health_background.full_clean()
        except ValidationError:
            self.fail("Test HealthBackground model should be valid")

    def test_condition_id_must_not_be_blank(self):
        self.health_background.condition_id = None
        with self.assertRaises(ValidationError):
            self.health_background.full_clean()

class ConversationIdModelTestCase(TestCase):
    def setUp(self):
        self.conversation_id = ConversationId(
            conversation_id = "20a922e9-3104-45e9-a185-a8a7befaabb5"
        )
    
    def test_valid_conversation_id(self):
        try:
            self.conversation_id.full_clean()
        except ValidationError:
            self.fail("Test ConversationId model should be valid")

    def test_conversation_id_must_not_be_blank(self):
        self.conversation_id.conversation_id = None
        with self.assertRaises(ValidationError):
            self.conversation_id.full_clean()

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


   

   