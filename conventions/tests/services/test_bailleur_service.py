import datetime

from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import ConventionBailleurForm
from conventions.models import Convention
from conventions.services import bailleurs, utils
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

    def test_update_bailleur_nom_error(self):
        self.service.request.POST = {
            "signataire_nom": "",
            "signataire_fonction": "DG",
            "signataire_date_deliberation": "2022-12-31",
        }
        self.service.update_bailleur()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertTrue(self.service.form.has_error("signataire_nom"))

    def test_update_bailleur_success(self):
        bailleur = self.service.convention.programme.bailleur
        bailleur_signataire_nom = bailleur.signataire_nom
        bailleur_signataire_fonction = bailleur.signataire_fonction
        bailleur_signataire_date_deliberation = bailleur.signataire_date_deliberation
        bailleur_signataire_bloc_signature = bailleur.signataire_bloc_signature

        self.service.request.POST = {
            "signataire_nom": "Johnny",
            "signataire_fonction": "Dirlo",
            "signataire_date_deliberation": "2022-02-01",
            "signataire_bloc_signature": "Mon Dirlo",
        }

        self.service.update_bailleur()
        bailleur.refresh_from_db()
        self.service.convention.refresh_from_db()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)
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

    def test_update_bailleur_success_signataire_perso(self):
        convention = self.service.convention

        self.service.request.POST = {
            "identification_bailleur": True,
            "identification_bailleur_detail": "Identification personalisée",
        }

        self.service.update_bailleur()
        convention.refresh_from_db()
        assert self.service.return_status == utils.ReturnStatus.SUCCESS
        assert convention.identification_bailleur
        assert (
            convention.identification_bailleur_detail == "Identification personalisée"
        )

    def test_should_add_siren(self):
        habilitation = {
            # …
            "groupe": {
                # …
                "profil": {
                    "code": "MO_PERS_MORALE",
                },
            },
            "porteeTerritComp": {
                # …
                "codePortee": "NAT",
                "regComp": None,
            },
            "statut": "VALIDEE",
        }
        self.assertTrue(self.service.should_add_sirens(habilitation))
        habilitation["statut"] = "A_VALIDER"
        self.assertFalse(self.service.should_add_sirens(habilitation))


def test_form_clean():
    form = ConventionBailleurForm(data={"identification_bailleur": False})
    form.is_valid()
    assert (
        form.errors["signataire_nom"][0]
        == "Le nom du signataire de la convention est obligatoire"
    )

    form = ConventionBailleurForm(data={"identification_bailleur": True})
    form.is_valid()
    assert (
        form.errors["identification_bailleur_detail"][0]
        == "Le détail de l'identification du bailleur est obligatoire "
        "lorsque vous avez choisi l'identification du bailleur personnalisée"
    )
