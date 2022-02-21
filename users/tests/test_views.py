from django.test import TestCase
from django.urls import reverse

from core.tests import utils_fixtures


class UserViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # pylint: disable=R0914
        utils_fixtures.create_all()

    def test_no_login(self):
        """
        If not login, the request is not redirected and buton to login are displayed
        """
        self.assertEqual("/", reverse("users:home"))
        response = self.client.get(reverse("users:home"))
        #        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Espace instructeur")
        self.assertContains(response, "Espace bailleur")
        self.assertNotContains(response, "Deconnexion")

        response = self.client.post(
            reverse("auth:login"),
            {"username": "sabine", "password": "faux mot de passe"},
        )
        self.assertEqual(response.status_code, 404)
        response = self.client.post(
            reverse("auth:login"), {"username": "sabine", "password": "12345"}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("users:home"))
        self.assertContains(response, "Deconnexion")
        self.assertNotContains(response, "Espace instructeur")
        self.assertNotContains(response, "Espace bailleur")
