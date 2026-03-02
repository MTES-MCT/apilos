from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractEditViewTestCase


class ConventionProgrammeViewTests(AbstractEditViewTestCase, TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
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
            "conventions:programme", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:cadastre", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/programme.html"
        self.error_payload = {
            "nom": "Fake Opération",
            "adresse": "",
            "code_postal": "01000",
            "ville": "Fake ville",
            "anru": "FALSE",
            "anah": "FALSE",
            "type_habitat": "INDIVIDUEL",
            "type_operation": "NEUF",
            "nb_locaux_commerciaux": "",
            "nb_bureaux": "",
            "autres_locaux_hors_convention": "",
        }
        self.success_payload = {
            "nom": "Fake Opération",
            "adresse": "123 rue du fake",
            "code_postal": "01000",
            "ville": "Fake ville",
            "anru": "FALSE",
            "anah": "FALSE",
            "type_habitat": "INDIVIDUEL",
            "type_operation": "NEUF",
            "nb_locaux_commerciaux": "",
            "nb_bureaux": "",
            "autres_locaux_hors_convention": "",
        }
        self.msg_prefix = "[ConventionProgrammeViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            self.convention_75.programme.adresse,
            "22 rue segur",
            msg=f"{self.msg_prefix}",
        )
        self.assertEqual(
            self.convention_75.adresse,
            "123 rue du fake",
            msg=f"{self.msg_prefix}",
        )

    def test_displays_seconde_vie_as_read_only_information(self):
        self.client.login(username="nicolas", password="12345")
        self.convention_75.programme.seconde_vie = True
        self.convention_75.programme.save(update_fields=["seconde_vie"])

        response = self.client.get(self.target_path)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Seconde vie")
        self.assertContains(response, 'name="seconde_vie"')
        self.assertContains(response, 'id="seconde_vie"')
        self.assertContains(response, "disabled")
