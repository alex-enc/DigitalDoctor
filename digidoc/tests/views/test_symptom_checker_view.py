"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from digidoc.models.symptom_checker_models import OnBoarding

class OnBoardingViewTestCase(TestCase):
    """Tests of the home view."""

    def setUp(self):
        self.url_on_boarding = reverse('on_boarding')
        self.name = 'John Doe'
        self.birth_year = 1990
        self.initial_symptoms = 'Cough, sore throat, runny nose'
        self.gender = 'Male'

    def test_on_boarding_url(self):
        self.assertEqual(self.url_on_boarding,'/on_boarding/')


class MainChatViewTestCase(TestCase):
    """Tests of the home view."""

    def setUp(self):
        self.url_main_chat = reverse('main_chat')

    def test_main_chat_url(self):
        self.assertEqual(self.url_main_chat, '/chat/')

