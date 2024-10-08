from django.test import TestCase
from django.urls import reverse

from conventions.models import Convention
from conventions.tests.views.abstract import AbstractEditViewTestCase
from users.models import User


class ConventionBailleurViewTests(AbstractEditViewTestCase, TestCase):
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
            "conventions:bailleur", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:programme", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/bailleur.html"
        self.error_payload = {
            "signataire_nom": "",
            "signataire_fonction": "DG",
            "signataire_date_deliberation": "2022-12-31",
        }
        self.success_payload = {
            "signataire_nom": "Lady Gaga",
            "signataire_fonction": "DG",
            "signataire_date_deliberation": "2022-12-31",
        }
        self.msg_prefix = "[ConventionBailleurViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            self.convention_75.signataire_nom,
            "Lady Gaga",
            msg=f"{self.msg_prefix}",
        )


class AvenantBailleurViewTests(ConventionBailleurViewTests):
    def setUp(self):
        super().setUp()
        # force convention_75 to be an avenant
        user = User.objects.get(username="fix")
        convention = Convention.objects.get(numero="0001")
        self.convention_75 = convention.clone(user, convention_origin=convention)
        self.target_path = reverse(
            "conventions:avenant_bailleur", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
        self.msg_prefix = "[AvenantBailleurViewTests] "
