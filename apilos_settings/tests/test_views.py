from django.test import TestCase
from django.urls import reverse

from core.tests import utils_fixtures


class ApilosSettingsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def test_display_bailleurs_or_administrations(self):
        """
        Superuser will display Profil, Administrations, Bailleurs and Utilisateurs in sidemenu
        Instructeur will display Profil, Administrations and Utilisateurs in sidemenu
        Bailleur will display Profil, Bailleurs and Utilisateurs in sidemenu
        """

        response = self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )
        response = self.client.get(reverse("settings:index"))
        self.assertRedirects(response, reverse("settings:users"))
        response = self.client.get(reverse("settings:users"))
        self.assertContains(response, "Votre profil")
        self.assertContains(response, "Administrations")
        self.assertContains(response, "Bailleurs")
        self.assertContains(response, "Utilisateurs")

        response = self.client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )

        response = self.client.get(reverse("settings:index"))
        self.assertRedirects(response, reverse("settings:administrations"))
        response = self.client.get(reverse("settings:administrations"))
        self.assertContains(response, "Votre profil")
        self.assertContains(response, "Administrations")
        self.assertContains(response, "Utilisateurs")
        self.assertNotContains(response, "Bailleurs")

        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(reverse("settings:index"))
        self.assertRedirects(response, reverse("settings:bailleurs"))
        response = self.client.get(reverse("settings:bailleurs"))
        self.assertContains(response, "Votre profil")
        self.assertContains(response, "Bailleurs")
        self.assertContains(response, "Utilisateurs")
        self.assertNotContains(response, "Administrations")

    def test_display_profile(self):
        """
        Superuser :
            won't display "Option d'envoi d'e-mail"
            will display "
        Bailleur :
            will display "Option d'envoi d'e-mail"
            will display "Administrateur de compte" active if true else inactive
        Instructeur :
            will display "Option d'envoi d'e-mail"
            will display "Administrateur de compte" active if true else inactive
        """
        response = self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertNotContains(response, "Option d'envoi d'e-mail")
        self.assertContains(response, "Administrateur de compte")
        self.assertContains(response, "Super Utilisateur")

        response = self.client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d'envoi d'e-mail")
        self.assertContains(response, "Administrateur de compte")
        self.assertNotContains(response, "Super Utilisateur")

        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d'envoi d'e-mail")
        self.assertContains(response, "Administrateur de compte")
        self.assertNotContains(response, "Super Utilisateur")
