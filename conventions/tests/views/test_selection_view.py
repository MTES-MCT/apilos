from django.test import TestCase
from django.urls import reverse

from bailleurs.models import Bailleur
from conventions.models import Convention, ConventionStatut
from conventions.tests.views.abstract import AbstractCreateViewTestCase
from instructeurs.models import Administration
from programmes.models import Financement, NatureLogement, TypeHabitat


class NewConventionAnruViewTests(AbstractCreateViewTestCase, TestCase):
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
        super().setUp()

        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        self.target_path = reverse("conventions:new_convention_anru")
        self.next_target_starts_with = "/conventions/bailleur"
        self.target_template = "conventions/new_convention_anru.html"
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
            "numero_operation": "123456789",
            "nom": "Programme de test",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "type_habitat": TypeHabitat.MIXTE,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "Bisouville",
        }
        self.msg_prefix = "[NewConventionAnruViewTests] "

    def _test_data_integrity(self):
        self.assertTrue(
            Convention.objects.get(
                programme__nom="Programme de test", lots__financement=Financement.PLUS
            ),
            msg=f"{self.msg_prefix}",
        )


class ConventionPostForAvenantViewTests(AbstractCreateViewTestCase, TestCase):
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
        super().setUp()

        bailleur = Bailleur.objects.get(siret="987654321")
        administration = Administration.objects.get(code="75000")
        self.target_path = reverse("conventions:search_for_avenant")
        self.next_target_starts_with = "/conventions/recapitulatif"
        self.target_template = "conventions/avenant/search_for_avenant.html"
        self.error_payload = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "financement": Financement.PLUS,
            "code_postal": "",
            "statut": ConventionStatut.SIGNEE.label,
            "numero": "2022-75-Rivoli-02-213",
        }
        self.success_payload = {
            "bailleur": str(bailleur.uuid),
            "administration": str(administration.uuid),
            "nom": "Programme de test",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "nb_logements": "10",
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "Bisouville",
            "statut": ConventionStatut.SIGNEE.label,
            "numero": "2022-75-Rivoli-02-213",
            "numero_avenant": "1",
        }
        self.msg_prefix = "[ConventionPostForAvenantViewTests] "

    def _test_data_integrity(self):
        self.assertTrue(
            Convention.objects.get(
                programme__nom="Programme de test",
                lots__financement=Financement.PLUS,
                parent_id__isnull=True,
            ),
            msg=f"{self.msg_prefix}",
        )
