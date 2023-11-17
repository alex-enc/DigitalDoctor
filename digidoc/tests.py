from django.test import TestCase
from .models import User
from django.core.exceptions import ValidationError

from django.contrib.auth.hashers import check_password
from django import forms
# from django.test import TestCase
from digidoc.forms import SignUpForm
from digidoc.models import User

# User model tests
class UserModelTestCase(TestCase):
    #tests whether the user created is valid
    def setUp(self):
        self.user = User.objects.create_user(
            'johndoe@example.org',
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

# Sign up form tests
# class SignUpFormTestCase(TestCase):
#     """Unit tests of the sign up form."""

#     def setUp(self):
#         self.form_input = {
#             'first_name': 'John',
#             'last_name': 'Doe',
#             'username': 'johndoe@example.org',
#             'email': 'johndoe@example.org',
#             'new_password': 'Password123',
#             'password_confirmation': 'Password123'
#         }

#     def test_valid_sign_up_form(self):
#         form = SignUpForm(data=self.form_input)
#         self.assertTrue(form.is_valid())

#     def test_form_has_necessary_fields(self):
#         form = SignUpForm()
#         self.assertIn('first_name', form.fields)
#         self.assertIn('last_name', form.fields)
#         self.assertIn('username', form.fields)
#         self.assertIn('email', form.fields)
#         email_field = form.fields['email']
#         self.assertTrue(isinstance(email_field, forms.EmailField))
#         self.assertIn('new_password', form.fields)
#         new_password_widget = form.fields['new_password'].widget
#         self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
#         self.assertIn('password_confirmation', form.fields)
#         password_confirmation_widget = form.fields['password_confirmation'].widget
#         self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

#     def test_form_uses_model_validation(self):
#         self.form_input['username'] = 'badusername'
#         form = SignUpForm(data=self.form_input)
#         self.assertFalse(form.is_valid())

#     def test_password_must_contain_uppercase_character(self):
#         self.form_input['new_password'] = 'password123'
#         self.form_input['password_confirmation'] = 'password123'
#         form = SignUpForm(data=self.form_input)
#         self.assertFalse(form.is_valid())

#     def test_password_must_contain_lowercase_character(self):
#         self.form_input['new_password'] = 'PASSWORD123'
#         self.form_input['password_confirmation'] = 'PASSWORD123'
#         form = SignUpForm(data=self.form_input)
#         self.assertFalse(form.is_valid())

#     def test_password_must_contain_number(self):
#         self.form_input['new_password'] = 'PasswordABC'
#         self.form_input['password_confirmation'] = 'PasswordABC'
#         form = SignUpForm(data=self.form_input)
#         self.assertFalse(form.is_valid())

#     def test_new_password_and_password_confirmation_are_identical(self):
#         self.form_input['password_confirmation'] = 'WrongPassword123'
#         form = SignUpForm(data=self.form_input)
#         self.assertFalse(form.is_valid())

#     def test_form_must_save_correctly(self):
#         form = SignUpForm(data=self.form_input)
#         before_count = User.objects.count()
#         form.save()
#         after_count = User.objects.count()
#         self.assertEqual(after_count, before_count+1)
#         user = User.objects.get(username='johndoe@example.org')
#         self.assertEqual(user.first_name, 'John')
#         self.assertEqual(user.last_name, 'Doe')
#         self.assertEqual(user.email, 'johndoe@example.org')
#         is_password_correct = check_password('Password123', user.password)
#         self.assertTrue(is_password_correct)