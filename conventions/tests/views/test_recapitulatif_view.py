from unittest.mock import patch

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

    def test_post_param_calls_the_correct_service_method(self):
        self.client.login(username="nicolas", password="12345")

        for post_param, expected in (
            ("update_programme_number", "update_programme_number"),
            ("update_convention_number", "update_convention_number"),
            ("cancel_convention", "cancel_convention"),
            ("reactive_convention", "reactive_convention"),
            (None, "save_convention_TypeIandII"),
        ):
            with patch(
                "conventions.views.conventions.ConventionRecapitulatifService",
                autospec=True,
            ) as mock_service:
                response = self.client.post(
                    self.target_path, data={post_param: "1"} if post_param else {}
                )
                self.assertEqual(response.status_code, 200)

            self.assertEqual(len(mock_service.method_calls), 1)
            self.assertEqual(mock_service.method_calls[0][0], f"().{expected}")
