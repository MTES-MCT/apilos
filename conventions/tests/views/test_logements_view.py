from django.test import TestCase
from django.urls import reverse

from conventions.models import Convention
from conventions.tests.fixtures import logement_success_payload
from conventions.tests.views.abstract import AbstractEditViewTestCase
from users.models import User


class ConventionLogementsViewTests(AbstractEditViewTestCase, TestCase):
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
            "conventions:logements", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:annexes", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/logements.html"
        self.error_payload = {
            "nb_logements": "2",
            "uuid": str(self.convention_75.lot.uuid),
            **logement_success_payload,
            "form-1-loyer": "750.00",
        }
        self.success_payload = {
            "nb_logements": "2",
            "uuid": str(self.convention_75.lot.uuid),
            **logement_success_payload,
        }
        self.msg_prefix = "[ConventionLogementsViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            self.convention_75.lot.nb_logements,
            2,
            msg=f"{self.msg_prefix}  2 logements",
        )
        self.assertEqual(
            self.convention_75.lot.logements.count(),
            2,
            msg=f"{self.msg_prefix} 2 logements",
        )


class AvenantLogementsViewTests(ConventionLogementsViewTests):
    def setUp(self):
        super().setUp()
        # force convention_75 to be an avenant
        user = User.objects.get(username="fix")
        convention = Convention.objects.get(numero="0001")
        self.convention_75 = convention.clone(user, convention_origin=convention)
        self.target_path = reverse(
            "conventions:avenant_logements", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:avenant_annexes", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/logements.html"
        self.msg_prefix = "[AvenantLogementsViewTests] "
