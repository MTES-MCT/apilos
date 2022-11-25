from bs4 import BeautifulSoup

from django.test import TestCase
from django.urls import reverse

from core.tests import utils_fixtures


class ConventionIndexViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def test_get_list(self):
        """
        Test displaying convention list as superuser without filter nor order
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.get(reverse("conventions:index"))
        soup = BeautifulSoup(response.content, 'html.parser')
        galion_refs = soup.find_all(attrs={'data-test-role': "programme-galion-cell"})
        financements = soup.find_all(attrs={'data-test-role': "programme-financement-cell"})

        self.assertListEqual([r.text for r in galion_refs], ['12345', '12345', '98765', '98765'])
        self.assertListEqual([f.text for f in financements], ['PLUS', 'PLAI', 'PLUS', 'PLAI'])

    def test_get_list_ordered_by_bailleur(self):
        """
        Test displaying convention list as superuser without filter but with bailleur order
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.get(reverse("conventions:index"), data={'order_by': "programme__bailleur__nom"})
        soup = BeautifulSoup(response.content, 'html.parser')
        galion_refs = soup.find_all(attrs={'data-test-role': "programme-galion-cell"})
        financements = soup.find_all(attrs={'data-test-role': "programme-financement-cell"})

        self.assertListEqual([r.text for r in galion_refs], ['12345', '12345', '98765', '98765'])
        self.assertListEqual([f.text for f in financements], ['PLUS', 'PLAI', 'PLUS', 'PLAI'])