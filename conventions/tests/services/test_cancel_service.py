from django.http import HttpRequest
from django.test import TestCase

from conventions.models import Convention
from conventions.models.choices import ConventionStatut
from conventions.services import recapitulatif
from users.models import User


class ConventionCancelServiceTest(TestCase):
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
        self.convention = Convention.objects.get(numero="0001")

    def test_instructeur_cancel_convention_projet(self):
        request = HttpRequest()
        request.user = User.objects.get(username="roger")
        recapitulatif.convention_cancel(request, self.convention)
        self.convention.refresh_from_db()
        self.assertTrue(self.convention.statut, ConventionStatut.ANNULEE.label)

    def test_bailleur_cancel_convention_projet(self):
        request = HttpRequest()
        request.user = User.objects.get(username="raph")
        recapitulatif.convention_cancel(request, self.convention)
        self.convention.refresh_from_db()
        self.assertTrue(self.convention.statut, ConventionStatut.ANNULEE.label)
