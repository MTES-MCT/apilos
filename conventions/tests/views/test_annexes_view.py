from django.test import TestCase
from django.urls import reverse
from conventions.models import Convention

from conventions.tests.views.abstract import AbstractEditViewTestCase
from programmes.models import Annexe, Logement, TypologieLogement
from users.models import User


class ConventionAnnexesViewTests(AbstractEditViewTestCase, TestCase):
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
        for designation in ["B1", "B2"]:
            Logement.objects.create(
                designation=designation,
                lot=self.convention_75.lot,
                typologie=TypologieLogement.T1,
                surface_habitable=10.00,
                surface_annexes=10.00,
                surface_annexes_retenue=5.00,
                surface_utile=15.00,
                loyer_par_metre_carre=5,
                coeficient=1.0000,
                loyer=75.00,
            )
        self.target_path = reverse(
            "conventions:annexes", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:stationnements", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/annexes.html"
        self.error_payload = {
            "uuid": self.convention_75.lot.uuid,
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "2",
            "form-0-uuid": "",
            "form-0-typologie": "TERRASSE",
            "form-0-logement_designation": "B1",
            "form-0-logement_typologie": "T1",
            "form-0-surface_hors_surface_retenue": "5.00",
            "form-0-loyer_par_metre_carre": "0.2",
            "form-0-loyer": "1.00",
            "form-1-uuid": "",
            "form-1-typologie": "TERRASSE",
            "form-1-logement_designation": "B2",
            "form-1-logement_typologie": "T1",
            "form-1-surface_hors_surface_retenue": "5.00",
            "form-1-loyer_par_metre_carre": "0.2",
            "form-1-loyer": "10.00",
            "annexe_caves": "FALSE",
            "annexe_soussols": "FALSE",
            "annexe_remises": "FALSE",
            "annexe_ateliers": "FALSE",
            "annexe_sechoirs": "FALSE",
            "annexe_celliers": "FALSE",
            "annexe_resserres": "on",
            "annexe_combles": "on",
            "annexe_balcons": "FALSE",
            "annexe_loggias": "FALSE",
            "annexe_terrasses": "FALSE",
        }
        self.success_payload = {
            "uuid": self.convention_75.lot.uuid,
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "2",
            "form-0-uuid": "",
            "form-0-typologie": "TERRASSE",
            "form-0-logement_designation": "B1",
            "form-0-logement_typologie": "T1",
            "form-0-surface_hors_surface_retenue": "5.00",
            "form-0-loyer_par_metre_carre": "0.2",
            "form-0-loyer": "1.00",
            "form-1-uuid": "",
            "form-1-typologie": "TERRASSE",
            "form-1-logement_designation": "B2",
            "form-1-logement_typologie": "T1",
            "form-1-surface_hors_surface_retenue": "5.00",
            "form-1-loyer_par_metre_carre": "0.2",
            "form-1-loyer": "1.00",
            "annexe_caves": "FALSE",
            "annexe_soussols": "FALSE",
            "annexe_remises": "FALSE",
            "annexe_ateliers": "FALSE",
            "annexe_sechoirs": "FALSE",
            "annexe_celliers": "FALSE",
            "annexe_resserres": "on",
            "annexe_combles": "on",
            "annexe_balcons": "FALSE",
            "annexe_loggias": "FALSE",
            "annexe_terrasses": "FALSE",
        }
        self.msg_prefix = "[ConventionAnnexesViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertTrue(
            self.convention_75.lot.annexe_combles,
            msg=f"{self.msg_prefix} ",
        )
        self.assertFalse(
            self.convention_75.lot.annexe_balcons,
            msg=f"{self.msg_prefix} ",
        )
        annexes = Annexe.objects.filter(
            logement__in=self.convention_75.lot.logements.all()
        )
        self.assertEqual(
            annexes.count(),
            2,
            msg=f"{self.msg_prefix} 2 annexes",
        )


class AvenantAnnexesViewTests(ConventionAnnexesViewTests):
    def setUp(self):
        super().setUp()
        # force convention_75 to be an avenant
        user = User.objects.get(username="fix")
        convention = Convention.objects.get(numero="0001")
        self.convention_75 = convention.clone(user, convention_origin=convention)
        self.target_path = reverse(
            "conventions:avenant_annexes", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
        self.msg_prefix = "[AvenantAnnexesViewTests] "
