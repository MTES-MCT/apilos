from django.http import HttpRequest
from django.test import TestCase
from conventions.forms.convention_number import ConventionNumberForm
from conventions.forms.programme_number import ProgrammeNumberForm
from conventions.models import Convention
from conventions.services import (
    recapitulatif,
)
from users.models import User


class ConventionRecapitulatifServiceTests(TestCase):
    fixtures = [
        "auth.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self):
        request = HttpRequest()
        self.convention = Convention.objects.get(numero="0001")
        request.user = User.objects.get(username="fix")
        self.service = recapitulatif.ConventionRecapitulatifService(
            convention=self.convention, request=request
        )

    def test_get_convention_recapitulatif(self):
        result = self.service.get_convention_recapitulatif()

        self.assertIsInstance(result["conventionNumberForm"], ConventionNumberForm)
        self.assertEqual(
            result["conventionNumberForm"].initial["convention_numero"],
            self.service.convention.numero,
        )

        self.assertIsInstance(result["programmeNumberForm"], ProgrammeNumberForm)
        self.assertEqual(
            result["programmeNumberForm"].initial["numero_galion"],
            self.service.convention.programme.numero_galion,
        )

    def test_update_programme_number_success(self):

        self.service.request.POST = {
            "numero_galion": "0" * 255,
            "update_programme_number": "1",
        }
        self.service.update_programme_number()

        self.assertEqual(self.convention.programme.numero_galion, "0" * 255)

    def test_update_programme_number_failed(self):

        self.service.request.POST = {
            "numero_galion": "0" * 256,
            "update_programme_number": "1",
        }
        result = self.service.update_programme_number()

        self.assertFalse(result["conventionNumberForm"].has_error("numero_galion"))
