from bs4 import BeautifulSoup

from django.test import TestCase
from django.urls import reverse


class ConventionIndexViewTests(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def test_get_index(self):
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.get(reverse("conventions:index"))
        self.assertRedirects(response, reverse("conventions:search_active"))

    def test_get_list_active(self):
        """
        Test displaying convention list as superuser without filter nor order
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.get(reverse("conventions:search_active"))
        soup = BeautifulSoup(response.content, "html.parser")
        galion_refs = soup.find_all(attrs={"data-test-role": "programme-galion-cell"})
        financements = soup.find_all(
            attrs={"data-test-role": "programme-financement-cell"}
        )

        self.assertEqual(len(galion_refs), 4)
        self.assertEqual(len(financements), 4)
        self.assertEqual({r.text.strip() for r in galion_refs}, {"12345", "98765"})
        self.assertEqual({f.text.strip() for f in financements}, {"PLAI", "PLUS"})

    def test_get_list_active_ordered_by_bailleur(self):
        """
        Test displaying convention list as superuser without filter but with bailleur order
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.get(
            reverse("conventions:search_active"),
            data={"order_by": "programme__bailleur__nom"},
        )
        soup = BeautifulSoup(response.content, "html.parser")
        galion_refs = soup.find_all(attrs={"data-test-role": "programme-galion-cell"})
        financements = soup.find_all(
            attrs={"data-test-role": "programme-financement-cell"}
        )

        self.assertEqual({r.text.strip() for r in galion_refs}, {"12345", "98765"})
        self.assertEqual({f.text.strip() for f in financements}, {"PLUS", "PLAI"})
