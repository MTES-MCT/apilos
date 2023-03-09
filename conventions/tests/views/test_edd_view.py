from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractEditViewTestCase


class ConventionEDDViewTests(AbstractEditViewTestCase, TestCase):
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
        self.target_path = reverse("conventions:edd", args=[self.convention_75.uuid])
        self.next_target_path = reverse(
            "conventions:financement", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/edd.html"
        self.error_payload = {
            "edd_volumetrique": "",
            "edd_volumetrique_files": "{}",
            "mention_publication_edd_volumetrique": "",
            "edd_classique": "",
            "edd_classique_files": "{}",
            "mention_publication_edd_classique": "",
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 1,
            "form-0-uuid": "",
            "form-0-designation": "A",
            "form-0-numero_lot": "1",
        }
        self.success_payload = {
            "edd_volumetrique": "",
            "edd_volumetrique_files": "{}",
            "mention_publication_edd_volumetrique": "",
            "edd_classique": "",
            "edd_classique_files": "{}",
            "mention_publication_edd_classique": "",
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-designation": "A",
            "form-0-numero_lot": "1",
            "form-0-financement": "PLUS",
            "form-1-uuid": "",
            "form-1-designation": "B",
            "form-1-numero_lot": "2",
            "form-1-financement": "PLAI",
        }
        self.msg_prefix = "[ConventionEDDViewTests] "

    def _test_data_integrity(self):
        pass
