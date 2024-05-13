from django.test import Client, TestCase
from django.urls import reverse


class ApilosSettingsViewTests(TestCase):
    fixtures = [
        "auth.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def test_sidemenu_is_superuser(self):
        response = self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )

        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Administrations")
        self.assertContains(response, "Bailleurs")
        self.assertContains(response, "Utilisateurs")

    def test_sidemenu_is_bailleur(self):
        client = Client()
        session = client.session
        session["bailleur"] = {"id": 1}
        session.save()

        response = client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = client.get(reverse("settings:profile"))
        self.assertContains(response, "Vos notifications")
        self.assertContains(response, "Votre entité bailleur")

    def test_sidemenu_is_instructeur(self):
        client = Client()
        session = client.session
        session["administration"] = {"id": 1}
        session.save()

        response = client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )

        response = client.get(reverse("settings:profile"))
        self.assertContains(response, "Vos notifications")
        self.assertContains(response, "Votre administration")

    def test_display_profile(self):
        response = self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertNotContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertContains(response, "Pas de préférences")

        response = self.client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertNotContains(response, "Super Utilisateur")

        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertNotContains(response, "Super Utilisateur")
