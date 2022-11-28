from django.test import TestCase
from django.urls import reverse

from conventions.tests.views.abstract import AbstractEditViewTestCase

post_fixture = {
    "form-TOTAL_FORMS": "2",
    "form-INITIAL_FORMS": "2",
    "form-0-uuid": "",
    "form-0-designation": "B1",
    "form-0-typologie": "T1",
    "form-0-surface_habitable": "12.12",
    "form-0-surface_annexes": "45.57",
    "form-0-surface_annexes_retenue": "0.00",
    "form-0-surface_utile": "30.00",
    "form-0-loyer_par_metre_carre": "4.5",
    "form-0-coeficient": "1.0000",
    "form-0-loyer": "135.00",
    "form-1-uuid": "",
    "form-1-designation": "B2",
    "form-1-typologie": "T1",
    "form-1-surface_habitable": "30.00",
    "form-1-surface_annexes": "0.00",
    "form-1-surface_annexes_retenue": "0.00",
    "form-1-surface_utile": "30.00",
    "form-1-loyer_par_metre_carre": "4.5",
    "form-1-coeficient": "1.0000",
    "form-1-loyer": "135.00",
    "loyer_derogatoire": "10",
    "lgts_mixite_sociale_negocies": "2",
}


class ConventionLogementsViewTests(AbstractEditViewTestCase, TestCase):
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
            **post_fixture,
            "form-1-loyer": "750.00",
        }
        self.success_payload = {
            "nb_logements": "2",
            "uuid": str(self.convention_75.lot.uuid),
            **post_fixture,
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
        self.target_path = reverse(
            "conventions:avenant_logements", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:avenant_annexes", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/logements.html"
        self.msg_prefix = "[AvenantLogementsViewTests] "
