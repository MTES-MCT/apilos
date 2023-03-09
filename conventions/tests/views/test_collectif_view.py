from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractEditViewTestCase
from conventions.tests.fixtures import collectif_success_payload
from programmes.models import NatureLogement


class ConventionCollectifViewTests(AbstractEditViewTestCase, TestCase):
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

        # convention is foyer
        self.convention_75.programme.nature_logement = NatureLogement.AUTRE
        self.convention_75.programme.save()

        self.target_path = reverse(
            "conventions:collectif", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:foyer_attribution", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/collectif.html"
        self.error_payload = {
            **collectif_success_payload,
            "form-1-nombre": "",
        }
        self.success_payload = collectif_success_payload

        self.msg_prefix = "[ConventionCollectifViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            float(self.convention_75.lot.foyer_residence_nb_garage_parking),
            2,
            msg=f"{self.msg_prefix}",
        )
