from django.http import HttpRequest
from django.test import TestCase

from conventions.models import Convention
from conventions.models.choices import ConventionStatut
from conventions.services import recapitulatif
from users.models import User


class ConventionCancelServiceTest(TestCase):
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
        self.convention = Convention.objects.get(numero="0001")

    def test_cancel_convention(self):
        request = HttpRequest()
        for username in ["roger", "raph"]:
            request.user = User.objects.get(username=username)
            service_recap = recapitulatif.ConventionRecapitulatifService(
                convention=self.convention, request=request
            )
            for statut in [
                ConventionStatut.PROJET.label,
                ConventionStatut.INSTRUCTION.label,
                ConventionStatut.CORRECTION.label,
            ]:
                self.convention.statut = statut
                self.convention.save()
                service_recap.cancel_convention()
                self.convention.refresh_from_db()
                self.assertEqual(self.convention.statut, ConventionStatut.ANNULEE.label)

            for statut in [
                ConventionStatut.A_SIGNER.label,
                ConventionStatut.SIGNEE.label,
                ConventionStatut.RESILIEE.label,
                ConventionStatut.DENONCEE.label,
            ]:
                self.convention.statut = statut
                self.convention.save()
                service_recap.cancel_convention()
                self.convention.refresh_from_db()
                self.assertEqual(self.convention.statut, statut)

    def test_reactive_convention(self):
        request = HttpRequest()
        for username in ["roger", "raph"]:
            request.user = User.objects.get(username=username)
            service_recap = recapitulatif.ConventionRecapitulatifService(
                convention=self.convention, request=request
            )
            for statut in [
                ConventionStatut.PROJET.label,
                ConventionStatut.INSTRUCTION.label,
                ConventionStatut.CORRECTION.label,
                ConventionStatut.A_SIGNER.label,
                ConventionStatut.SIGNEE.label,
                ConventionStatut.RESILIEE.label,
                ConventionStatut.DENONCEE.label,
            ]:
                self.convention.statut = statut
                self.convention.save()
                service_recap.reactive_convention()
                self.convention.refresh_from_db()
                self.assertEqual(self.convention.statut, statut)

            self.convention.statut = ConventionStatut.ANNULEE.label
            self.convention.save()
            service_recap.reactive_convention()
            self.convention.refresh_from_db()
            self.assertEqual(self.convention.statut, ConventionStatut.PROJET.label)
