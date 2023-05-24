from django.test import TestCase, override_settings, modify_settings
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

    @override_settings(CERBERE_MOCKED=True)
    @override_settings(CERBERE_AUTH="/cerbere/login")
    @modify_settings(
        AUTHENTICATION_BACKENDS={"append": "core.backends.MockedCerbereCASBackend"}
    )
    @modify_settings(INSTALLED_APPS={"append": "cerbere"})
    @override_settings(NO_SIAP_MENU=True)
    @override_settings(USE_MOCKED_SIAP_CLIENT=True)
    def test_view_instructeur_cerebere_ok(self):
        self.skipTest("overriden settings cant be applied to urlcong")
        # login as user_instructeur_paris
        response = self.client.get(
            "/accounts/cerbere-login", {"ticket": "sabine.cerbere"}
        )
        self.assertRedirects(response, "/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("recapitulatif", ["f590c593-e37f-4258-b38a-f8d2869969c4"])
        )
        self.assertEqual(response.status_code, 200)
