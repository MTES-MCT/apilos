from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from instructeurs.models import Administration
from users.models import User


class CreateInstructeurCommandTests(TestCase):
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

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "create_instructeur",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_create_success_ddt_with_delegataire(self):
        self.call_command("Martin", "Jean", "jean.martin@instructeur.paris", "DD075")

        instructeur = User.objects.get(username="jean.martin@instructeur.paris")
        self.assertEqual(instructeur.first_name, "Jean")
        self.assertEqual(instructeur.last_name, "Martin")
        self.assertEqual(instructeur.email, "jean.martin@instructeur.paris")
        self.assertTrue(instructeur.is_instructeur())
        self.assertIsNotNone(instructeur.password)
        # L'instructeur de la DDT doit être créé et activé avec vue sur sa DDT ainsi que ses délégataires
        self.assertEqual(
            ["DD075", "75000"],
            [administration.code for administration in instructeur.administrations()],
        )

    def test_create_success_delegataire(self):
        self.call_command(
            "Garnier", "Jeanne", "jeanne.garnier@instructeur.paris", "75000"
        )

        instructrice = User.objects.get(username="jeanne.garnier@instructeur.paris")
        self.assertEqual(instructrice.first_name, "Jeanne")
        self.assertEqual(instructrice.last_name, "Garnier")
        self.assertEqual(instructrice.email, "jeanne.garnier@instructeur.paris")
        self.assertTrue(instructrice.is_instructeur())
        self.assertIsNotNone(instructrice.password)
        # L'instructrice du délégataire doit être créée et activée avec vue uniquement sur son administration
        self.assertEqual(
            ["75000"],
            [administration.code for administration in instructrice.administrations()],
        )

    def test_create_skipped(self):
        with self.assertRaises(Administration.DoesNotExist):
            # Cet instructeur ne doit pas être créé, car aucune administration ne correspond à ce code
            self.call_command("Martin", "Jean", "jean.martin@inconnu.fr", "INCON")

    def test_create_failure(self):
        with self.assertRaises(ValidationError):
            # Cet instructeur ne doit pas être créé, car l'adresse email est invaldie
            self.call_command("Martin", "Jean", "not@validnemail", "75000")
