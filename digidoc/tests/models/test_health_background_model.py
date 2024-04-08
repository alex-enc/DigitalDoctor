from django.test import TestCase
from digidoc.models.symptom_checker_models import HealthBackground
from django.core.exceptions import ValidationError

# tests for the HealthBackground model
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