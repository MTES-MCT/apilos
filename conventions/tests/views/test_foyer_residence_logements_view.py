from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractEditViewTestCase
from conventions.tests.fixtures import foyer_residence_logements_success_payload
from programmes.models import NatureLogement


class ConventionLogementsViewTests(AbstractEditViewTestCase, TestCase):
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

        self.convention_75.programme.nature_logement = NatureLogement.AUTRE
        self.convention_75.programme.save()
        self.convention_75.lot.nb_logements = 2
        self.convention_75.lot.save()

        self.target_path = reverse(
            "conventions:foyer_residence_logements", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:collectif", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/foyer_residence_logements.html"
        self.error_payload = {
            **foyer_residence_logements_success_payload,
            "surface_habitable_totale": "1",
            # FIXME "nb_logements": "2",
        }
        self.success_payload = foyer_residence_logements_success_payload

        self.msg_prefix = "[ConventionFoyerResidenceLogementsViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            float(self.convention_75.lot.surface_habitable_totale),
            50.55,
            msg=f"{self.msg_prefix}",
        )
        self.assertEqual(
            self.convention_75.lot.logements.count(),
            2,
            msg=f"{self.msg_prefix} 2 logements",
        )
