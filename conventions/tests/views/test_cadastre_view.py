from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractEditViewTestCase


class ConventionCadastreViewTests(AbstractEditViewTestCase, TestCase):
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
            "conventions:cadastre", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:edd", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/cadastre.html"
        self.error_payload = {
            "permis_construire": "",
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 0,
            "form-0-uuid": "",
            "form-0-section": "",
            "form-0-numero": "13",
            "form-0-lieudit": "Marseille",
            "form-0-surface": "0 ha 1 a 27 ca",
            "form-1-uuid": "",
            "form-1-section": "AC",
            "form-1-numero": "15",
            "form-1-lieudit": "Marseille",
            "form-1-surface": "0 ha 1 a 2 ca",
            "effet_relatif_files": "{}",
            "acte_de_propriete_files": "{}",
            "certificat_adressage_files": "{}",
        }
        self.success_payload = {
            "permis_construire": "",
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 0,
            "form-0-uuid": "",
            "form-0-section": "AC",
            "form-0-numero": "13",
            "form-0-lieudit": "Marseille",
            "form-0-surface": "0 ha 1 a 27 ca",
            "form-1-uuid": "",
            "form-1-section": "AC",
            "form-1-numero": "15",
            "form-1-lieudit": "Marseille",
            "form-1-surface": "0 ha 1 a 2 ca",
            "effet_relatif_files": "{}",
            "acte_de_propriete_files": "{}",
            "certificat_adressage_files": "{}",
        }
        self.msg_prefix = "[ConventionCadastreViewTests] "

    def _test_data_integrity(self):
        pass
