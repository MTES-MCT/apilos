from django.http import HttpRequest
from django.test import TestCase
from django.core.exceptions import NON_FIELD_ERRORS

from conventions.forms import ConventionFoyerVariantesForm
from conventions.models import Convention
from conventions.tests.fixtures import variantes_success_payload
from conventions.services import (
    variantes,
    utils,
)
from programmes.models import NatureLogement
from users.models import User


class ConventionFoyerVarianteServiceTests(TestCase):
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

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        convention.programme.nature_logement = NatureLogement.AUTRE
        convention.programme.save()
        request.user = User.objects.get(username="fix")
        self.service = variantes.ConventionFoyerVariantesService(
            convention=convention, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, ConventionFoyerVariantesForm)
        self.assertEqual(
            self.service.form.initial["uuid"],
            self.service.convention.uuid,
        )

    def test_save_success(self):

        self.service.request.POST = variantes_success_payload
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

    def test_save_failed_variantes(self):

        self.service.request.POST = {
            "foyer_residence_variante_1": "FALSE",
            "foyer_residence_variante_2": "FALSE",
            "foyer_residence_variante_3": "FALSE",
        }
        self.service.save()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)

        self.assertFalse(
            self.service.form.has_error("foyer_residence_variante_2_travaux")
        )
        self.assertTrue(self.service.form.has_error(NON_FIELD_ERRORS))

    def test_save_failed_travaux_without_its_variante(self):

        self.service.request.POST = {
            "foyer_residence_variante_1": "on",
            "foyer_residence_variante_2": "on",
            "foyer_residence_variante_2_travaux": "",
            "foyer_residence_variante_3": "on",
        }
        self.service.save()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)

        self.assertTrue(
            self.service.form.has_error("foyer_residence_variante_2_travaux")
        )
        self.assertFalse(self.service.form.has_error(NON_FIELD_ERRORS))
