from django.test import TestCase
from .models import User
from django.core.exceptions import ValidationError

# Create your tests here.
class UserModelTestCase(TestCase):
    #tests whether the user created is valid
    def setUp(self):
        self.user = User.objects.create_user(
            'johndoe',
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.org',
            password = 'Password123',
        )
        
    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()