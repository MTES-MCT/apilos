from django.test import TestCase
from django.urls import reverse

from conventions.models import Convention, Preteur
from conventions.tests.views.abstract import AbstractEditViewTestCase
from programmes.models import NatureLogement
from users.models import User


class ConventionFinancementViewTests(AbstractEditViewTestCase, TestCase):
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
        prets = self.convention_75.prets
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

    def test_next_step_when_foyer(self):
        self.convention_75.programme.nature_logement = NatureLogement.AUTRE
        self.convention_75.programme.save()
        foyer_next_target_path = reverse(
            "conventions:foyer_residence_logements", args=[self.convention_75.uuid]
        )

        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path, self.success_payload)
        self.assertEqual(response.status_code, 302, msg=f"{self.msg_prefix}")
        self.assertRedirects(
            response, foyer_next_target_path, msg_prefix=self.msg_prefix
        )


class AvenantFinancementViewTests(ConventionFinancementViewTests):
    def setUp(self):
        super().setUp()
        # force convention_75 to be an avenant
        user = User.objects.get(username="fix")
        convention = Convention.objects.get(numero="0001")
        self.convention_75 = convention.clone(user, convention_origin=convention)
        self.target_path = reverse(
            "conventions:avenant_financement", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )

    def test_next_step_when_foyer(self):
        self.convention_75.programme.nature_logement = NatureLogement.AUTRE
        self.convention_75.programme.save()

        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path, self.success_payload)
        self.assertEqual(response.status_code, 302, msg=f"{self.msg_prefix}")
        self.assertRedirects(
            response, self.next_target_path, msg_prefix=self.msg_prefix
        )
