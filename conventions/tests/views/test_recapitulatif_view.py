import os

from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractCreateViewTestCase


class ConventionRecapitulatifTests(AbstractCreateViewTestCase, TestCase):
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
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
        self.post_success_http_code = 200
        self.target_template = "conventions/recapitulatif.html"
        self.error_payload = {
            "numero_galion": "0" * 256,
            "update_programme_number": "1",
        }
        self.success_payload = {
            "numero_galion": "0" * 255,
            "update_programme_number": "1",
        }
        self.msg_prefix = "[ConventionRecapitulatifTests] "

    def tearDown(self) -> None:
        self.client.session.clear()

    def test_view_instructeur_cerbere_ok(self):
        self.client.get(
            reverse("cas_ng_login", "core.urls.siap"),
            data={"ticket": "sabine.cerbere", "next": "/"},
            SERVER_NAME="test.apilos.logement.fr",
        )

        response = self.client.get(
            reverse(
                "conventions:recapitulatif",
                "core.urls.siap",
                ["f590c593-e37f-4258-b38a-f8d2869969c4"],
            ),
            data={"habilitation_id": 3},
            SERVER_NAME="test.apilos.logement.fr",
        )
        self.assertEqual(response.status_code, 200)
