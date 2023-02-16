from django.test import TestCase
from django.urls import reverse
from conventions.models import (
    Convention,
    ConventionStatut,
)

from conventions.tests.views.abstract import AbstractCreateViewTestCase
from bailleurs.models import Bailleur
from instructeurs.models import Administration
from programmes.models import Financement, NatureLogement, TypeHabitat
from core.tests import utils_fixtures


class ConventionSelectionFromDBViewTests(AbstractCreateViewTestCase, TestCase):
    def setUp(self):
        super().setUp()

        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        programme_2 = utils_fixtures.create_programme(
            bailleur, administration, nom="Programme 2"
        )
        utils_fixtures.create_lot(programme_2, Financement.PLAI)
        self.lot_plus_2 = utils_fixtures.create_lot(programme_2, Financement.PLUS)

        self.target_path = reverse("conventions:selection")
        self.next_target_starts_with = "/conventions/bailleur"
        self.target_template = "conventions/selection_from_db.html"
        self.error_payload = {
            # "lot": str(self.convention.lot.uuid)
        }
        self.success_payload = {
            "lot": str(self.lot_plus_2.uuid),
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
        }
        self.msg_prefix = "[ConventionSelectionFromDBViewTests] "

    def _test_data_integrity(self):
        self.assertTrue(
            Convention.objects.get(lot=self.lot_plus_2),
            msg=f"{self.msg_prefix}",
        )

    def test_view_superuser(self):
        # login as superuser
        response = self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")


class ConventionSelectionFromZeroViewTests(AbstractCreateViewTestCase, TestCase):
    fixtures = ["departements.json"]

    def setUp(self):
        super().setUp()

        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        self.target_path = reverse("conventions:selection_from_zero")
        self.next_target_starts_with = "/conventions/bailleur"
        self.target_template = "conventions/selection_from_zero.html"
        self.error_payload = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "type_habitat": TypeHabitat.MIXTE,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "",
        }
        self.success_payload = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "type_habitat": TypeHabitat.MIXTE,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "Bisouville",
        }
        self.msg_prefix = "[ConventionSelectionFromZeroViewTests] "

    def _test_data_integrity(self):
        self.assertTrue(
            Convention.objects.get(
                programme__nom="Programme de test", financement=Financement.PLUS
            ),
            msg=f"{self.msg_prefix}",
        )


class ConventionPostForAvenantViewTests(AbstractCreateViewTestCase, TestCase):
    fixtures = ["departements.json"]

    def setUp(self):
        super().setUp()

        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        self.target_path = reverse("conventions:search_for_avenant_result")
        self.next_target_starts_with = "/conventions/recapitulatif"
        self.target_template = "conventions/avenant/search_for_avenant_result.html"
        self.error_payload = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "financement": Financement.PLUS,
            "code_postal": "",
            "statut": ConventionStatut.SIGNEE,
            "numero": "2022-75-Rivoli-02-213",
        }
        self.success_payload = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "statut": ConventionStatut.SIGNEE,
            "numero": "2022-75-Rivoli-02-213",
            "numero_avenant": "1",
        }
        self.msg_prefix = "[ConventionPostForAvenantViewTests] "

    def _test_data_integrity(self):
        self.assertTrue(
            Convention.objects.get(
                programme__nom="Programme de test",
                financement=Financement.PLUS,
                parent_id__isnull=True,
            ),
            msg=f"{self.msg_prefix}",
        )
