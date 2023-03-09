import random

from django.http import HttpRequest
from django.test import TestCase

from conventions.forms import ConventionFoyerAttributionForm
from conventions.models import Convention
from conventions.tests.fixtures import foyer_attribution_success_payload
from conventions.services import (
    foyer_attribution,
    utils,
)
from programmes.models import NatureLogement
from users.models import User


class ConventionFoyerAttributionServiceTests(TestCase):
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
        convention.programme.nature_logement = NatureLogement.AUTRE
        convention.programme.save()
        request.user = User.objects.get(username="fix")
        self.service = foyer_attribution.ConventionFoyerAttributionService(
            convention=convention, request=request
        )

    def test_get(self):
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, ConventionFoyerAttributionForm)
        self.assertEqual(
            self.service.form.initial["uuid"],
            self.service.convention.uuid,
        )

    def test_get_type_agees(self):
        for field in [
            "attribution_handicapes_foyer",
            "attribution_handicapes_foyer_de_vie",
            "attribution_handicapes_foyer_medicalise",
            "attribution_handicapes_autre",
        ]:
            setattr(
                self.service.convention,
                field,
                False,
            )

        setattr(
            self.service.convention,
            random.choice(
                [
                    "attribution_agees_autonomie",
                    "attribution_agees_ephad",
                    "attribution_agees_desorientees",
                    "attribution_agees_petite_unite",
                    "attribution_agees_autre",
                ]
            ),
            True,
        )
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertEqual(
            self.service.form.initial["attribution_type"],
            "agees",
        )

    def test_get_type_handicapes(self):
        for field in [
            "attribution_agees_autonomie",
            "attribution_agees_ephad",
            "attribution_agees_desorientees",
            "attribution_agees_petite_unite",
            "attribution_agees_autre",
        ]:
            setattr(
                self.service.convention,
                field,
                False,
            )

        setattr(
            self.service.convention,
            random.choice(
                [
                    "attribution_handicapes_foyer",
                    "attribution_handicapes_foyer_de_vie",
                    "attribution_handicapes_foyer_medicalise",
                    "attribution_handicapes_autre",
                ]
            ),
            True,
        )
        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertEqual(
            self.service.form.initial["attribution_type"],
            "handicapes",
        )

    def test_get_type_inclusif(self):
        for field in [
            "attribution_agees_autonomie",
            "attribution_agees_ephad",
            "attribution_agees_desorientees",
            "attribution_agees_petite_unite",
            "attribution_agees_autre",
            "attribution_handicapes_foyer",
            "attribution_handicapes_foyer_de_vie",
            "attribution_handicapes_foyer_medicalise",
            "attribution_handicapes_autre",
        ]:
            setattr(
                self.service.convention,
                field,
                False,
            )

        self.service.get()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertEqual(
            self.service.form.initial["attribution_type"],
            "inclusif",
        )

    def test_save_success(self):

        self.service.request.POST = foyer_attribution_success_payload
        self.service.save()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.SUCCESS)

    def test_save_failed_needed_fields(self):

        self.service.request.POST = {}
        self.service.save()

        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)

        self.assertTrue(
            self.service.form.has_error("attribution_reservation_prefectorale")
        )
        self.assertTrue(self.service.form.has_error("attribution_type"))
        self.assertFalse(self.service.form.has_error("attribution_agees_autonomie"))
        self.assertFalse(self.service.form.has_error("attribution_agees_ephad"))
        self.assertFalse(self.service.form.has_error("attribution_agees_desorientees"))
        self.assertFalse(self.service.form.has_error("attribution_agees_petite_unite"))
        self.assertFalse(self.service.form.has_error("attribution_agees_autre"))
        self.assertFalse(self.service.form.has_error("attribution_agees_autre"))
        self.assertFalse(self.service.form.has_error("attribution_agees_autre_detail"))
        self.assertFalse(self.service.form.has_error("attribution_handicapes_foyer"))
        self.assertFalse(
            self.service.form.has_error("attribution_handicapes_foyer_de_vie")
        )
        self.assertFalse(
            self.service.form.has_error("attribution_handicapes_foyer_medicalise")
        )
        self.assertFalse(self.service.form.has_error("attribution_handicapes_autre"))
        self.assertFalse(
            self.service.form.has_error("attribution_handicapes_autre_detail")
        )
        self.assertFalse(
            self.service.form.has_error("attribution_inclusif_conditions_specifiques")
        )
        self.assertFalse(
            self.service.form.has_error("attribution_inclusif_conditions_admission")
        )
        self.assertFalse(
            self.service.form.has_error("attribution_inclusif_modalites_attribution")
        )
        self.assertFalse(
            self.service.form.has_error("attribution_inclusif_partenariats")
        )
        self.assertFalse(self.service.form.has_error("attribution_inclusif_activites"))
        self.assertTrue(
            self.service.form.has_error("attribution_modalites_reservations")
        )
        self.assertTrue(
            self.service.form.has_error("attribution_modalites_choix_personnes")
        )
        self.assertFalse(
            self.service.form.has_error("attribution_prestations_integrees")
        )
        self.assertFalse(
            self.service.form.has_error("attribution_prestations_facultatives")
        )

    def test_save_failed_needed_fields_when_inclusif(self):
        self.service.request.POST = {
            **foyer_attribution_success_payload,
            "attribution_type": "inclusif",
            "attribution_inclusif_conditions_specifiques": "",
            "attribution_inclusif_conditions_admission": "",
            "attribution_inclusif_modalites_attribution": "",
            "attribution_inclusif_partenariats": "",
            "attribution_inclusif_activites": "",
        }
        self.service.save()
        self.assertTrue(
            self.service.form.has_error("attribution_inclusif_conditions_specifiques")
        )
        self.assertTrue(
            self.service.form.has_error("attribution_inclusif_conditions_admission")
        )
        self.assertTrue(
            self.service.form.has_error("attribution_inclusif_partenariats")
        )
        self.assertTrue(self.service.form.has_error("attribution_inclusif_activites"))

    def test_save_failed_needed_autre_details_agees(self):
        self.service.request.POST = {
            **foyer_attribution_success_payload,
            "attribution_type": "agees",
            "attribution_agees_autre": "on",
            "attribution_agees_autre_detail": "",
        }
        self.service.save()
        self.assertTrue(self.service.form.has_error("attribution_agees_autre_detail"))

    def test_save_failed_needed_autre_details_handicapes(self):
        self.service.request.POST = {
            **foyer_attribution_success_payload,
            "attribution_type": "handicapes",
            "attribution_handicapes_autre": "on",
            "attribution_handicapes_autre_detail": "",
        }
        self.service.save()
        self.assertTrue(
            self.service.form.has_error("attribution_handicapes_autre_detail")
        )
