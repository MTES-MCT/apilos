from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import ProgrammeForm
from conventions.models import Convention
from conventions.services import services_programmes, utils
from users.models import User


class ConventionProgrammeServiceTests(TestCase):
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

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        request.user = User.objects.get(username="fix")
        self.service = services_programmes.ConventionProgrammeService(
            convention=convention, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, ProgrammeForm)
        programme = self.service.convention.programme
        self.assertEqual(
            self.service.form.initial["uuid"],
            programme.uuid,
        )
        self.assertEqual(self.service.form.initial["nom"], programme.nom)
        # Initialise avec l'adresse du programme si la convention n'a pas d'adresse
        self.assertEqual(self.service.form.initial["adresse"], programme.adresse)
        self.assertEqual(
            self.service.form.initial["code_postal"], programme.code_postal
        )
        self.assertEqual(self.service.form.initial["ville"], programme.ville)

    def test_get_with_convention_adresse(self):
        self.service.convention.adresse = "123 rue du fake"
        self.service.convention.programme.code_postal = "02000"
        self.service.convention.programme.ville = "Fake ville"
        self.service.convention.save()

        self.service.get()

        # Initialise avec l'adresse de la convention si définie
        self.assertEqual(self.service.form.initial["adresse"], "123 rue du fake")
        self.assertEqual(self.service.form.initial["code_postal"], "02000")
        self.assertEqual(self.service.form.initial["ville"], "Fake ville")

    def test_save(self):
        programme = self.service.convention.programme

        self.service.request.POST = {
            "nom": "Fake Opération",
            "adresse": "",
            "code_postal": "01000",
            "ville": "Fake ville",
            "nb_logements": "28",
            "anru": "FALSE",
            "anah": "FALSE",
            "type_habitat": "INDIVIDUEL",
            "type_operation": "NEUF",
            "nb_locaux_commerciaux": "",
            "nb_bureaux": "",
            "autres_locaux_hors_convention": "",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.form.has_error("adresse"))

        self.service.request.POST = {
            "nom": "Fake Opération",
            "adresse": "123 rue du fake",
            "nb_logements": "28",
            "anru": "FALSE",
            "anah": "FALSE",
            "type_habitat": "INDIVIDUEL",
            "type_operation": "NEUF",
            "nb_locaux_commerciaux": "",
            "nb_bureaux": "",
            "autres_locaux_hors_convention": "",
        }

        self.service.save()
        programme.refresh_from_db()
        self.service.convention.refresh_from_db()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        self.assertEqual(programme.nom, "Fake Opération")
        # L'adresse du programme reste inchangée
        self.assertEqual(programme.adresse, "22 rue segur")
        self.assertEqual(programme.code_postal, "75007")
        self.assertEqual(programme.ville, "Paris")
        # L'adresse de la convention est mise à jour
        self.assertEqual(self.service.convention.adresse, "123 rue du fake")
