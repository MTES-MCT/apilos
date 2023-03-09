import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from bailleurs.models import Bailleur
from users.models import User


class ApilosSettingsViewTests(TestCase):
    fixtures = [
        "auth.json",
        # "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

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
        self.assertNotContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertNotContains(response, "Filtrer par départements")
        self.assertContains(response, "Administrateur de compte")
        self.assertContains(response, "Super Utilisateur")

        response = self.client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertNotContains(response, "Filtrer par départements")
        self.assertContains(response, "Administrateur de compte")
        self.assertNotContains(response, "Super Utilisateur")

        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertContains(response, "Filtrer par départements")
        self.assertContains(response, "Administrateur de compte")
        self.assertNotContains(response, "Super Utilisateur")

    def test_create_bailleur(self):
        """
        Superuser will log in & create a new bailleur
        """

        # login as superuser
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        bailleur = Bailleur.objects.get(siret="987654321")

        response = self.client.post(
            reverse("settings:add_user"),
            {
                "email": "bailleur@apilos.com",
                "username": "bailleur.test",
                "first_name": "Bail",
                "last_name": "Leur",
                "preferences_email": "PARTIEL",
                "telephone": "0612345678",
                "administrateur_de_compte": False,
                "is_superuser": False,
                "user_type": "BAILLEUR",
                "bailleur": bailleur.uuid,
            },
        )

        self.assertRedirects(response, reverse("settings:users"))
        new_user = User.objects.get(username="bailleur.test")

        self.assertFalse(new_user.is_superuser)
        self.assertTrue(new_user.is_bailleur())
        self.assertEqual("nicolas", new_user.creator.username)

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
