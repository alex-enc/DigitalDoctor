"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from digidoc.models.user_models import User

class HomeViewTestCase(TestCase):
    """Tests of the home view."""

    def setUp(self):
        self.url = reverse('home')

    def test_home_url(self):
        self.assertEqual(self.url,'/')

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
