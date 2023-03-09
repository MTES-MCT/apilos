import datetime

from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import ConventionBailleurForm
from conventions.models import Convention
from conventions.services import (
    bailleurs,
    utils,
)
from users.models import User


class ConventionBailleurServiceTests(TestCase):
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
        request.user = User.objects.get(username="fix")
        self.service = bailleurs.ConventionBailleurService(
            convention=convention, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, ConventionBailleurForm)
        bailleur = self.service.convention.programme.bailleur
        self.assertEqual(
            self.service.form.initial["uuid"],
            bailleur.uuid,
        )
        self.assertEqual(self.service.form.initial["nom"], bailleur.nom)

    def test_save(self):

        bailleur = self.service.convention.programme.bailleur
        bailleur_signataire_nom = bailleur.signataire_nom
        bailleur_signataire_fonction = bailleur.signataire_fonction
        bailleur_signataire_date_deliberation = bailleur.signataire_date_deliberation
        bailleur_signataire_bloc_signature = bailleur.signataire_bloc_signature

        self.service.request.POST = {
            "nom": "",
            "adresse": "fake_address",
            "code_postal": "01000",
        }
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.form.has_error("nom"))

        self.service.request.POST = {
            "nom": "nom bailleur",
            "adresse": "fake_address",
            "code_postal": "01000",
            "signataire_nom": "Johnny",
            "signataire_fonction": "Dirlo",
            "signataire_date_deliberation": "2022-02-01",
            "signataire_bloc_signature": "Mon Dirlo",
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
        self.assertEqual(
            bailleur.signataire_bloc_signature, bailleur_signataire_bloc_signature
        )
        self.assertEqual(self.service.convention.signataire_nom, "Johnny")
        self.assertEqual(self.service.convention.signataire_fonction, "Dirlo")
        self.assertEqual(
            self.service.convention.signataire_date_deliberation,
            datetime.date(2022, 2, 1),
        )
        self.assertEqual(self.service.convention.signataire_bloc_signature, "Mon Dirlo")
