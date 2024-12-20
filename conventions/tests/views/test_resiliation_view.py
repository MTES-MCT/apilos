from django.test import TestCase
from django.urls import reverse

from conventions.models.convention import Convention
from conventions.tests.factories import ConventionFactory
from users.models import User


class ConventionResiliationTests(TestCase):
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

    def test_resiliation_validate_redirect(self):
        avenant = self.convention.clone(
            User.objects.get(username="nicolas"), convention_origin=self.convention
        )
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.post(
            f"/conventions/resiliation_validate/{avenant.uuid}",
        )

        self.assertEqual(
            response["Location"], f"/conventions/post_action/{avenant.uuid}"
        )

    def test_resiliation_start_inspecteur_departemental(self):
        convention = ConventionFactory(create_lot=True)
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.post(
            f"/conventions/resiliation_start/{convention.uuid}",
            {"avenant_type": "resiliation"},
        )

        # redirected to url for instructeurs départementaux only
        assert "/conventions/resiliation/" in response["Location"]

    def test_resiliation_start_bailleur(self):
        convention = ConventionFactory(create_lot=True)
        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )

        response = self.client.post(
            f"/conventions/resiliation_start/{convention.uuid}",
            {"avenant_type": "resiliation"},
        )

        # redirected to url for bailleurs and instructeurs délégataires
        assert "/conventions/resiliation_creation/" in response["Location"]

    def test_resiliation_start_instructeur(self):
        convention = ConventionFactory(create_lot=True)

        response = self.client.post(
            reverse("login"), {"username": "sabine", "password": "12345"}
        )
        response = self.client.post(
            f"/conventions/resiliation_start/{convention.uuid}",
            {"avenant_type": "resiliation"},
        )

        # redirected to url for bailleurs and instructeurs délégataires
        assert "/conventions/resiliation_creation/" in response["Location"]
