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
