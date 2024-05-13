import os

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from bailleurs.models import Bailleur


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

    def test_import_bailleur_users_upload_ok(self):
        """
        Superuser will log in & upload a xlsx listing file
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        with open(
            os.path.join(
                os.path.dirname(__file__), "./resources/listing_bailleur_ok.xlsx"
            ),
            "rb",
        ) as listing_file:
            response = self.client.post(
                reverse("settings:import_bailleur_users"),
                {
                    "file": listing_file,
                    "Upload": True,
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_import_bailleur_users_upload_ko(self):
        """
        Superuser will log in & upload an invalid xlsx listing file
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        with open(
            os.path.join(
                os.path.dirname(__file__),
                "./resources/listing_bailleur_missing_nom_bailleur.xlsx",
            ),
            "rb",
        ) as listing_file:
            response = self.client.post(
                reverse("settings:import_bailleur_users"),
                {
                    "file": listing_file,
                    "Upload": True,
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_import_bailleur_users_submit_ok(self):
        """
        Superuser will log in & submit a list of bailleurs users to create
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.post(reverse("settings:import_bailleur_users"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bailleur = Bailleur.objects.get(nom="HLM")

        response = self.client.post(
            reverse("settings:import_bailleur_users"),
            {
                "form-TOTAL_FORMS": 1,
                "form-INITIAL_FORMS": 1,
                "form-0-first_name": "Jean",
                "form-0-last_name": "Bailleur",
                "form-0-username": "jean.bailleur2",
                "form-0-bailleur": bailleur.id,
                "form-0-email": "jean.bailleur2@apilos.com",
                "form-1-first_name": "Jeanne",
                "form-1-last_name": "Bailleur",
                "form-1-username": "jeanne.bailleur2",
                "form-1-bailleur": bailleur.id,
                "form-1-email": "jeanne.bailleur2@apilos.com",
                "form-2-first_name": "Chantal",
                "form-2-last_name": "Bailleur",
                "form-2-username": "chantal.bailleur",
                "form-2-bailleur": bailleur.id,
                "form-2-email": "chantal.bailleur2@apilos.com",
            },
        )
        self.assertRedirects(response, reverse("settings:users"))

    def test_import_bailleur_users_submit_nok(self):
        """
        Superuser will log in & submit a list of bailleurs users to create
        """
        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.post(reverse("settings:import_bailleur_users"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bailleur = Bailleur.objects.get(nom="HLM")

        response = self.client.post(
            reverse("settings:import_bailleur_users"),
            {
                "form-TOTAL_FORMS": 1,
                "form-INITIAL_FORMS": 1,
                "form-0-first_name": "Sabine",
                "form-0-last_name": "L'autre",
                "form-0-username": "sabine",
                "form-0-bailleur": bailleur.id,
                "form-0-email": "sabine@apilos.com",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
