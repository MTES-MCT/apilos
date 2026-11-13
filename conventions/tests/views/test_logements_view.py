from bs4 import BeautifulSoup
from django.test import TestCase
from django.urls import reverse

from conventions.models import Convention
from conventions.tests.fixtures import logement_success_payload
from conventions.tests.views.abstract import AbstractEditViewTestCase
from programmes.models import Logement
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

    def _corrigee_sans_loyer_payload(self):
        lot = self.convention_75.lot
        lot.logements.all().delete()
        logements = [
            Logement.objects.create(
                lot=lot,
                designation=f"CS{index}",
                typologie="T1",
                surface_habitable="30.00",
                surface_corrigee="35.00",
                import_order=index,
            )
            for index in range(2)
        ]
        payload = {
            **self.success_payload,
            "avec_loyer-TOTAL_FORMS": "0",
            "avec_loyer-INITIAL_FORMS": "0",
            "formset_disabled": "1",
            "formset_sans_loyer_disabled": "1",
            "formset_corrigee_disabled": "1",
            "formset_corrigee_sans_loyer_disabled": "",
            "corrigee_sans_loyer-TOTAL_FORMS": "2",
            "corrigee_sans_loyer-INITIAL_FORMS": "2",
            "ignore_optional_errors": "1",
        }
        for index, logement in enumerate(logements):
            prefix = f"corrigee_sans_loyer-{index}"
            payload.update(
                {
                    f"{prefix}-uuid": str(logement.uuid),
                    f"{prefix}-designation": logement.designation,
                    f"{prefix}-typologie": "T1",
                    f"{prefix}-financement": lot.financement,
                    f"{prefix}-surface_habitable": "30.00",
                    f"{prefix}-surface_corrigee": "35.00",
                    f"{prefix}-import_order": str(index),
                }
            )
        return payload

    def test_corrigee_sans_loyer_can_be_saved_with_other_sections_empty(self):
        payload = self._corrigee_sans_loyer_payload()
        self._login_as_superuser()
        page = BeautifulSoup(self.client.get(self.target_path).content, "html.parser")
        for prefix in ("avec_loyer", "sans_loyer", "corrigee_avec_loyer"):
            for field in ("TOTAL_FORMS", "INITIAL_FORMS"):
                self.assertEqual(
                    page.find("input", attrs={"name": f"{prefix}-{field}"})["value"],
                    "0",
                )
        self.assertEqual(page.find(id="id_formset_disabled")["value"], "1")
        self.assertEqual(
            page.find(id="id_formset_corrigee_sans_loyer_disabled")["value"], ""
        )
        self.assertTrue(page.find(id="toggle-corrigee-sans-loyer").has_attr("checked"))

        for prefix in ("avec_loyer", "sans_loyer", "corrigee_avec_loyer"):
            payload[f"{prefix}-TOTAL_FORMS"] = ""
            payload[f"{prefix}-INITIAL_FORMS"] = ""
        payload["corrigee_sans_loyer-0-surface_corrigee"] = "42.00"
        response = self.client.post(self.target_path, payload)

        self.assertRedirects(response, self.next_target_path)
        logements = self.convention_75.lot.logements.order_by("designation")
        self.assertEqual(logements.count(), 2)
        self.assertEqual(str(logements[0].surface_corrigee), "42.00")

    def test_disabled_section_is_deleted_even_if_its_rows_are_invalid(self):
        payload = self._corrigee_sans_loyer_payload()
        payload["formset_corrigee_sans_loyer_disabled"] = "1"
        payload["corrigee_sans_loyer-0-designation"] = ""
        for prefix in ("avec_loyer", "sans_loyer", "corrigee_avec_loyer"):
            payload[f"{prefix}-TOTAL_FORMS"] = ""
            payload[f"{prefix}-INITIAL_FORMS"] = ""
        self._login_as_superuser()

        response = self.client.post(self.target_path, payload)

        self.assertRedirects(response, self.next_target_path)
        self.assertFalse(self.convention_75.lot.logements.exists())

    def test_disabled_section_stays_unchecked_after_another_validation_error(self):
        payload = self._corrigee_sans_loyer_payload()
        payload["formset_corrigee_sans_loyer_disabled"] = "1"
        payload["lots-0-nb_logements"] = ""
        self._login_as_superuser()

        response = self.client.post(self.target_path, payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.convention_75.lot.logements.count(), 2)
        page = BeautifulSoup(response.content, "html.parser")
        self.assertFalse(page.find(id="toggle-corrigee-sans-loyer").has_attr("checked"))
        self.assertEqual(
            page.find(id="id_formset_corrigee_sans_loyer_disabled")["value"], "1"
        )

        payload["lots-0-nb_logements"] = "2"
        response = self.client.post(self.target_path, payload)
        self.assertRedirects(response, self.next_target_path)
        self.assertFalse(self.convention_75.lot.logements.exists())

    def test_disabling_corrigee_sans_loyer_preserves_other_sections(self):
        payload = self._corrigee_sans_loyer_payload()
        payload.update(
            {
                key: value
                for key, value in logement_success_payload.items()
                if key.startswith("avec_loyer-")
            }
        )
        payload["formset_disabled"] = ""
        payload["formset_corrigee_sans_loyer_disabled"] = "1"
        self._login_as_superuser()

        response = self.client.post(self.target_path, payload)

        self.assertRedirects(response, self.next_target_path)
        logements = self.convention_75.lot.logements
        self.assertEqual(logements.count(), 2)
        self.assertSetEqual(
            set(logements.values_list("designation", flat=True)), {"B1", "B2"}
        )

    def test_corrigee_sans_loyer_is_saved_and_deleted_across_lots(self):
        payload = self._corrigee_sans_loyer_payload()
        second_lot = self.convention_75.lots.create(financement="PLS", nb_logements=1)
        logement = self.convention_75.lot.logements.get(designation="CS1")
        logement.lot = second_lot
        logement.save()
        payload.update(
            {
                "lots-TOTAL_FORMS": "2",
                "lots-INITIAL_FORMS": "2",
                "lots-0-nb_logements": "1",
                "lots-1-uuid": str(second_lot.uuid),
                "lots-1-financement": "PLS",
                "lots-1-nb_logements": "1",
                "corrigee_sans_loyer-1-financement": "PLS",
            }
        )
        self._login_as_superuser()

        response = self.client.post(self.target_path, payload)

        self.assertRedirects(response, self.next_target_path)
        self.assertEqual(self.convention_75.lot.logements.count(), 1)
        self.assertEqual(second_lot.logements.count(), 1)
        self.assertTrue(second_lot.logements.filter(uuid=logement.uuid).exists())

        payload["formset_corrigee_sans_loyer_disabled"] = "1"
        response = self.client.post(self.target_path, payload)
        self.assertRedirects(response, self.next_target_path)
        self.assertFalse(
            Logement.objects.filter(lot__convention=self.convention_75).exists()
        )

    def test_new_corrigee_sans_loyer_rows_are_created_once_across_lots(self):
        payload = self._corrigee_sans_loyer_payload()
        self.convention_75.lot.logements.all().delete()
        second_lot = self.convention_75.lots.create(financement="PLS", nb_logements=1)
        payload.update(
            {
                "lots-TOTAL_FORMS": "2",
                "lots-INITIAL_FORMS": "2",
                "lots-0-nb_logements": "1",
                "lots-1-uuid": str(second_lot.uuid),
                "lots-1-financement": "PLS",
                "lots-1-nb_logements": "1",
                "corrigee_sans_loyer-0-uuid": "",
                "corrigee_sans_loyer-1-uuid": "",
                "corrigee_sans_loyer-1-financement": "PLS",
            }
        )
        self._login_as_superuser()

        response = self.client.post(self.target_path, payload)

        self.assertRedirects(response, self.next_target_path)
        self.assertEqual(self.convention_75.lot.logements.count(), 1)
        self.assertEqual(second_lot.logements.count(), 1)

    def test_active_section_with_invalid_row_is_not_saved(self):
        payload = self._corrigee_sans_loyer_payload()
        payload["corrigee_sans_loyer-0-surface_corrigee"] = ""
        self._login_as_superuser()

        response = self.client.post(self.target_path, payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La surface corrigée est obligatoire")
        self.assertEqual(self.convention_75.lot.logements.count(), 2)

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
