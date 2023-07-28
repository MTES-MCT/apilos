from django.test import TestCase
from django.urls import reverse

from conventions.forms.convention_form_administration import (
    UpdateConventionAdministrationForm,
)
from conventions.models.convention import Convention
from conventions.tests.views.abstract import AbstractCreateViewTestCase
from conventions.views.conventions import get_forms_for_convention


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

    def test_update_administration_redirect(self):
        convention = Convention.objects.get(uuid="f590c593-e37f-4258-b38a-f8d2869969c4")
        forms = get_forms_for_convention(convention)
        assert "update_convention_administration_form" in forms

        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})
        response = self.client.post(
            f"/conventions/recapitulatif/{convention.uuid}",
            data={
                "convention": convention.pk,
                "administration": "8b21f223-7121-4304-87ab-e2873cc1dcc1",
                "verification": "transférer",
            },
        )

        self.assertEqual(response["Location"], "/conventions/en-cours")
        convention.refresh_from_db()
        self.assertEqual(
            str(convention.programme.administration.uuid),
            "8b21f223-7121-4304-87ab-e2873cc1dcc1",
        )

    def test_update_administration_basic(self):
        convention = Convention.objects.get(uuid="f590c593-e37f-4258-b38a-f8d2869969c4")
        form = UpdateConventionAdministrationForm(
            {
                "convention": convention.pk,
                "administration": "8b21f223-7121-4304-87ab-e2873cc1dcc1",
                "verification": "transférer",
            }
        )
        self.assertTrue(form.is_valid())

    def test_update_administration_verification(self):
        convention = Convention.objects.get(uuid="f590c593-e37f-4258-b38a-f8d2869969c4")
        form = UpdateConventionAdministrationForm(
            {
                "convention": convention.pk,
                "administration": "8b21f223-7121-4304-87ab-e2873cc1dcc1",
            }
        )

        self.assertEqual(
            form.errors["verification"],
            ["Vous devez recopier le mot pour valider l'opération"],
        )
