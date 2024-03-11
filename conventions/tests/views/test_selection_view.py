from django.test import TestCase
from django.urls import reverse

from bailleurs.models import Bailleur
from conventions.models import Convention
from conventions.tests.views.abstract import AbstractCreateViewTestCase
from instructeurs.models import Administration
from programmes.models import Financement, NatureLogement, TypeHabitat


class NewConventionViewTests(AbstractCreateViewTestCase, TestCase):
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
        self.target_path = reverse("conventions:new_convention")
        self.next_target_starts_with = "/conventions/bailleur"
        self.target_template = "conventions/new_convention.html"
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
            "numero_galion": "123456789",
            "nom": "Programme de test",
            "nb_logements": "10",
            "nature_logement": NatureLogement.LOGEMENTSORDINAIRES,
            "type_habitat": TypeHabitat.MIXTE,
            "financement": Financement.PLUS,
            "code_postal": "20000",
            "ville": "Bisouville",
        }
        self.msg_prefix = "[NewConventionViewTests] "

    def _test_data_integrity(self):
        self.assertTrue(
            Convention.objects.get(
                programme__nom="Programme de test", financement=Financement.PLUS
            ),
            msg=f"{self.msg_prefix}",
        )
