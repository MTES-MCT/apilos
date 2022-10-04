from django.test import TestCase
from django.urls import reverse

from bailleurs.models import Bailleur
from core.tests import utils_fixtures
from users.models import User


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
        self.assertNotContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertNotContains(response, "Filtrer par departements")
        self.assertContains(response, "Administrateur de compte")
        self.assertContains(response, "Super Utilisateur")

        response = self.client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertNotContains(response, "Filtrer par departements")
        self.assertContains(response, "Administrateur de compte")
        self.assertNotContains(response, "Super Utilisateur")

        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(reverse("settings:profile"))
        self.assertContains(response, "Option d&#x27;envoi d&#x27;e-mail")
        self.assertContains(response, "Filtrer par departements")
        self.assertContains(response, "Administrateur de compte")
        self.assertNotContains(response, "Super Utilisateur")

    def test_create_bailleur(self):
        """
        Superuser will login & create a new bailleur
        """

        # login as superuser
        self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )

        bailleur = Bailleur.objects.get(siret="987654321")

        response = self.client.post(reverse('settings:add_user'), {
            'email': "bailleur@apilos.com",
            'username': "bailleur.test",
            'first_name': "Bail",
            'last_name': "Leur",
            'preferences_email': "PARTIEL",
            'telephone': "0612345678",
            'administrateur_de_compte': False,
            'is_superuser': False,
            'user_type': "BAILLEUR",
            'bailleur': bailleur.uuid
        })

        print(response.content)
        self.assertRedirects(response, reverse("settings:users"))
        new_user = User.objects.get(username='bailleur.test')

        self.assertFalse(new_user.is_superuser)
        self.assertTrue(new_user.is_bailleur())
        self.assertEqual('nicolas', new_user.creator.username)
