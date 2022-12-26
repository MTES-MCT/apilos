from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from core.tests import utils_fixtures


class UserViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # pylint: disable=R0914
        utils_fixtures.create_all()
        settings.CERBERE = None

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
            reverse("login"),
            {"username": "sabine", "password": "faux mot de passe"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertFormError(
            response,
            "form",
            None,
            "Saisissez un nom d’utilisateur et un mot de passe valides. Remarquez que chacun de"
            + " ces champs est sensible à la casse (différenciation des majuscules/minuscules).",
        )
        response = self.client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("users:home"))
        self.assertRedirects(response, reverse("conventions:index"), fetch_redirect_response=False)
        response = self.client.get(reverse("conventions:index"))
        self.assertRedirects(response, reverse("conventions:search_active"), fetch_redirect_response=False)
        response = self.client.get(reverse("conventions:search_active"))

        self.assertContains(response, "Déconnexion")
        self.assertNotContains(response, "Espace instructeur")
        self.assertNotContains(response, "Espace bailleur")
