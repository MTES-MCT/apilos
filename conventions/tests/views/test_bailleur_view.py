from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractEditViewTestCase


class ConventionBailleurViewTests(AbstractEditViewTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.target_path = reverse(
            "conventions:bailleur", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:programme", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/bailleur.html"
        self.error_payload = {
            "nom": "",
            "adresse": "fake adresse",
            "code_postal": "00000",
        }
        self.success_payload = {
            "nom": "fake nom",
            "adresse": "fake adresse",
            "code_postal": "00000",
        }
        self.msg_prefix = "[ConventionBailleurViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            self.convention_75.lot.programme.bailleur.adresse,
            "fake adresse",
            msg=f"{self.msg_prefix}",
        )


class AvenantBailleurViewTests(ConventionBailleurViewTests):
    def setUp(self):
        super().setUp()
        self.target_path = reverse(
            "conventions:avenant_bailleur", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
        self.msg_prefix = "[AvenantBailleurViewTests] "
