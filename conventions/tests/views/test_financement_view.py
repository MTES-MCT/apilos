from django.test import TestCase
from django.urls import reverse

from conventions.models import Preteur
from conventions.tests.views.abstract import AbstractViewTestCase


class ConventionFinancementViewTests(AbstractViewTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.target_path = reverse(
            "conventions:financement", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:logements", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/financement.html"
        self.error_payload = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-numero": "A",
            "form-0-date_octroi": "2020-01-01",
            "form-0-duree": "50",
            "form-0-montant": "1000000.00",
            "form-0-preteur": "CDCF",
            "form-0-autre": "",
            "form-1-uuid": "",
            "form-1-numero": "A",
            "form-1-date_octroi": "2020-01-01",
            "form-1-duree": "",
            "form-1-montant": "200000.00",
            "form-1-preteur": "CDCL",
            "form-1-autre": "",
            "annee_fin_conventionnement": "2093",
            "fond_propre": "",
        }
        self.success_payload = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-numero": "A",
            "form-0-date_octroi": "2020-01-01",
            "form-0-duree": "50",
            "form-0-montant": "1000000.00",
            "form-0-preteur": "CDCF",
            "form-0-autre": "",
            "form-1-uuid": "",
            "form-1-numero": "A",
            "form-1-date_octroi": "2020-01-01",
            "form-1-duree": "20",
            "form-1-montant": "200000.00",
            "form-1-preteur": "CDCL",
            "form-1-autre": "",
            "annee_fin_conventionnement": "2093",
            "fond_propre": "",
        }
        self.msg_prefix = "[ConventionFinancementViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        prets = self.convention_75.pret_set
        self.assertEqual(
            prets.count(),
            2,
            msg=f"{self.msg_prefix} 2 prets after save",
        )
        self.assertEqual(
            [pret.preteur for pret in prets.all()],
            [Preteur.CDCF, Preteur.CDCL],
            msg=f"{self.msg_prefix} 2 prets CDC",
        )


class AvenantFinancementViewTests(ConventionFinancementViewTests):
    def setUp(self):
        super().setUp()
        self.target_path = reverse(
            "conventions:avenant_financement", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
