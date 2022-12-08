import datetime

from django.http import HttpRequest
from django.test import TestCase

from bailleurs.forms import BailleurForm
from conventions.models import Convention
from conventions.services import (
    services_bailleurs,
    utils,
)
from core.tests import utils_fixtures
from users.models import User


class ConventionBailleurServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        request = HttpRequest()
        convention = Convention.objects.get(numero="0001")
        request.user = User.objects.get(username="fix")
        self.service = services_bailleurs.ConventionBailleurService(
            convention=convention, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, BailleurForm)
        bailleur = self.service.convention.lot.programme.bailleur
        self.assertEqual(
            self.service.form.initial["uuid"],
            bailleur.uuid,
        )
        self.assertEqual(self.service.form.initial["nom"], bailleur.nom)

    def test_save(self):

        bailleur = self.service.convention.lot.programme.bailleur
        bailleur_signataire_nom = bailleur.signataire_nom
        bailleur_signataire_fonction = bailleur.signataire_fonction
        bailleur_signataire_date_deliberation = bailleur.signataire_date_deliberation

        self.service.request.POST = {
            "nom": "",
            "adresse": "fake_address",
            "code_postal": "00000",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.form.has_error("nom"))

        self.service.request.POST = {
            "nom": "nom bailleur",
            "adresse": "fake_address",
            "code_postal": "00000",
            "signataire_nom": "Johnny",
            "signataire_fonction": "Dirlo",
            "signataire_date_deliberation": "2022-02-01",
        }

        self.service.save()
        bailleur.refresh_from_db()
        self.service.convention.refresh_from_db()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
        self.assertEqual(bailleur.nom, "nom bailleur")
        self.assertEqual(bailleur.signataire_nom, bailleur_signataire_nom)
        self.assertEqual(bailleur.signataire_fonction, bailleur_signataire_fonction)
        self.assertEqual(
            bailleur.signataire_date_deliberation, bailleur_signataire_date_deliberation
        )
        self.assertEqual(self.service.convention.signataire_nom, "Johnny")
        self.assertEqual(self.service.convention.signataire_fonction, "Dirlo")
        self.assertEqual(
            self.service.convention.signataire_date_deliberation,
            datetime.date(2022, 2, 1),
        )
