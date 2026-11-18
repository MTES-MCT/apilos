from bs4 import BeautifulSoup
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
            "avec_loyer-1-loyer": "750.00",
        }
        self.success_payload = {
            "nb_logements": "2",
            "uuid": str(self.convention_75.lot.uuid),
            **logement_success_payload,
        }
        self.success_payload["lots-0-uuid"] = str(self.convention_75.lot.uuid)
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
        self.success_payload["lots-0-uuid"] = str(self.convention_75.lot.uuid)
        self.target_path = reverse(
            "conventions:avenant_logements", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:avenant_annexes", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/logements.html"
        self.msg_prefix = "[AvenantLogementsViewTests] "

    def test_only_the_table_with_errors_has_an_error_indicator(self):
        sections = {
            "avec_loyer": ("utile", "formset_disabled"),
            "sans_loyer": ("utile-sans-loyer", "formset_sans_loyer_disabled"),
            "corrigee_avec_loyer": ("corrigee", "formset_corrigee_disabled"),
            "corrigee_sans_loyer": (
                "corrigee-sans-loyer",
                "formset_corrigee_sans_loyer_disabled",
            ),
        }
        self._login_as_superuser()
        for prefix, (section, disabled_field) in sections.items():
            with self.subTest(section=section):
                payload = {
                    **self.success_payload,
                    "ignore_optional_errors": "1",
                    **{field: "1" for _, field in sections.values()},
                }
                for other_prefix in sections:
                    payload[f"{other_prefix}-TOTAL_FORMS"] = "0"
                    payload[f"{other_prefix}-INITIAL_FORMS"] = "0"
                for key, value in logement_success_payload.items():
                    if key.startswith("avec_loyer-0-"):
                        payload[key.replace("avec_loyer", prefix, 1)] = value
                payload.update(
                    {
                        disabled_field: "",
                        f"{prefix}-TOTAL_FORMS": "1",
                        f"{prefix}-INITIAL_FORMS": "1",
                        f"{prefix}-0-designation": "",
                        f"{prefix}-0-surface_corrigee": "35.00",
                    }
                )

                response = self.client.post(self.target_path, payload)

                self.assertEqual(response.status_code, 200)
                page = BeautifulSoup(response.content, "html.parser")
                for other_section, _ in sections.values():
                    table = page.select_one(f".table-{other_section} .fr-table")
                    self.assertEqual(
                        "apilos-table--error" in table.get("class", []),
                        other_section == section,
                    )
                    self.assertEqual(
                        bool(
                            table.find(
                                "p",
                                string="Ce tableau contient des erreurs. Veuillez corriger les champs concernés.",
                            )
                        ),
                        other_section == section,
                    )

    def test_initial_tables_have_no_error_indicator(self):
        self._login_as_superuser()
        response = self.client.get(self.target_path)
        page = BeautifulSoup(response.content, "html.parser")
        self.assertFalse(page.select(".apilos-table--error"))
