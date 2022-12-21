from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractEditViewTestCase
from conventions.tests.fixtures import collectif_success_payload
from programmes.models import NatureLogement


class ConventionCollectifViewTests(AbstractEditViewTestCase, TestCase):
    def setUp(self):
        super().setUp()

        # convention is foyer
        self.convention_75.programme.nature_logement = NatureLogement.AUTRE
        self.convention_75.programme.save()

        self.target_path = reverse(
            "conventions:collectif", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:attribution", args=[self.convention_75.uuid]
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
