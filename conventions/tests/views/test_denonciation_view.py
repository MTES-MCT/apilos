from django.test import TestCase
from django.urls import reverse

from conventions.forms.convention_form_denonciation import ConventionDenonciationForm
from conventions.models.convention import Convention
from users.models import User


class ConventionDenonciationTests(TestCase):
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
        self.convention = Convention.objects.get(
            uuid="f590c593-e37f-4258-b38a-f8d2869969c4"
        )
        self.avenant = self.convention.clone(
            User.objects.get(username="nicolas"), convention_origin=self.convention
        )

    def test_denonciation_validate_redirect(self):

        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})
        response = self.client.post(
            f"/conventions/denonciation_validate/{self.avenant.uuid}",
        )

        self.assertEqual(
            response["Location"], f"/conventions/post_action/{self.avenant.uuid}"
        )

    def test_denonciation_form(self):

        form = ConventionDenonciationForm({"uuid": self.avenant.uuid})

        self.assertEqual(
            form.errors["date_denonciation"],
            ["Vous devez saisir une date de dénonciation"],
        )
