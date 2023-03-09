from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import ConventionResidenceAttributionForm
from conventions.models import Convention
from conventions.tests.fixtures import residence_attribution_success_payload
from conventions.services import (
    residence_attribution,
    utils,
)
from programmes.models import NatureLogement
from users.models import User


class ConventionResidenceAttributionServiceTests(TestCase):
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
        convention.programme.nature_logement = NatureLogement.PENSIONSDEFAMILLE
        convention.programme.save()
        request.user = User.objects.get(username="fix")
        self.service = residence_attribution.ConventionResidenceAttributionService(
            convention=convention, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, ConventionResidenceAttributionForm)
        self.assertEqual(
            self.service.form.initial["uuid"],
            self.service.convention.uuid,
        )

    def test_save_success(self):

        self.service.request.POST = residence_attribution_success_payload
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

    def test_save_failed_needed_fields(self):

        self.service.request.POST = {}
        self.service.save()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)

        for not_requiered_field in [
            "attribution_residence_sociale_ordinaire",
            "attribution_pension_de_famille",
            "attribution_residence_accueil",
            "attribution_prestations_integrees",
            "attribution_prestations_facultatives",
        ]:
            self.assertFalse(
                self.service.form.has_error(not_requiered_field),
                f"{not_requiered_field} should not be required",
            )

        for requiered_field in [
            "attribution_reservation_prefectorale",
            "attribution_modalites_reservations",
            "attribution_modalites_choix_personnes",
        ]:
            self.assertTrue(
                self.service.form.has_error(requiered_field),
                f"{requiered_field} should be required",
            )
