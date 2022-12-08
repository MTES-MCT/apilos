from django.http import HttpRequest
from django.test import TestCase

from conventions.models import Convention
from conventions.services import (
    services_programmes,
    utils,
)
from core.tests import utils_fixtures
from programmes.forms import ProgrammeForm
from users.models import User


class ConventionProgrammeServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

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
        programme = self.service.convention.lot.programme
        self.assertEqual(
            self.service.form.initial["uuid"],
            programme.uuid,
        )
        self.assertEqual(self.service.form.initial["nom"], programme.nom)

    def test_save(self):

        programme = self.service.convention.lot.programme

        self.service.request.POST = {
            "nom": "Fake Opération",
            "adresse": "",
            "code_postal": "00000",
            "ville": "Fake ville",
            "nb_logements": "28",
            "anru": "FALSE",
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
            "code_postal": "00000",
            "ville": "Fake ville",
            "nb_logements": "28",
            "anru": "FALSE",
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
        self.assertEqual(programme.adresse, "123 rue du fake")
