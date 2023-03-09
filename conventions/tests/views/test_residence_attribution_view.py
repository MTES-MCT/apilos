from django.forms import model_to_dict
from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractEditViewTestCase
from conventions.tests.fixtures import residence_attribution_success_payload
from programmes.models import NatureLogement


class ConventionResidenceAttributionViewTests(AbstractEditViewTestCase, TestCase):
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
        super().setUp()
        self.target_path = reverse(
            "conventions:residence_attribution", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:variantes", args=[self.convention_75.uuid]
        )
        self.convention_75.programme.nature_logement = NatureLogement.RESIDENCEDACCUEIL
        self.convention_75.programme.save()
        self.target_template = "conventions/residence_attribution.html"
        self.error_payload = {
            **residence_attribution_success_payload,
            "attribution_reservation_prefectorale": "",
        }
        self.success_payload = residence_attribution_success_payload
        self.msg_prefix = "[ConventionResidenceAttributionViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            self.convention_75.attribution_reservation_prefectorale,
            10,
            msg=f"{self.msg_prefix}",
        )

        self.assertDictEqual(
            model_to_dict(
                self.convention_75,
                fields=[
                    "attribution_reservation_prefectorale",
                    "attribution_residence_sociale_ordinaire",
                    "attribution_pension_de_famille",
                    "attribution_residence_accueil",
                    "attribution_modalites_reservations",
                    "attribution_modalites_choix_personnes",
                    "attribution_prestations_integrees",
                    "attribution_prestations_facultatives",
                ],
            ),
            {
                "attribution_reservation_prefectorale": 10,
                "attribution_residence_sociale_ordinaire": True,
                "attribution_pension_de_famille": True,
                "attribution_residence_accueil": False,
                "attribution_modalites_reservations": "test",
                "attribution_modalites_choix_personnes": "Top !!!",
                "attribution_prestations_integrees": "OKOK",
                "attribution_prestations_facultatives": "",
            },
            msg=f"{self.msg_prefix}",
        )
