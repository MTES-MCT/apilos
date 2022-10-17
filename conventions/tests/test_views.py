from django.test import TestCase
from django.urls import reverse

from conventions.models import Convention
from core.tests import utils_fixtures


class AvenantCommentsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        self.convention_75 = Convention.objects.filter(numero="0001").first()
        self.target_path = reverse(
            "conventions:avenant_comments", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/avenant_comments.html"
        self.error_payload = {"comments": "O" * 5001}
        self.success_payload = {"comments": "This is a comment"}
        self.msg_prefix = "[AvenantCommentsViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            self.convention_75.comments,
            '{"files": [], "text": "This is a comment"}',
            msg=f"{self.msg_prefix}",
        )

    def test_AvenantCommentsView_not_logged(self):
        # user not logged -> redirect to login
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 302, msg=f"{self.msg_prefix}")
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={self.target_path}',
            msg_prefix=self.msg_prefix,
        )

    def test_AvenantCommentsView_superuser(self):
        # login as superuser
        response = self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200, msg=f"{self.msg_prefix}")

        response = self.client.post(
            self.target_path,
            self.success_payload,
        )
        self.assertEqual(response.status_code, 302, msg=f"{self.msg_prefix}")
        self.assertRedirects(
            response, self.next_target_path, msg_prefix=self.msg_prefix
        )
        self._test_data_integrity()

        response = self.client.post(
            self.target_path,
            self.error_payload,
        )
        self.assertEqual(response.status_code, 200, msg=f"{self.msg_prefix}")
        self.assertTemplateUsed(
            response, self.target_template, msg_prefix=self.msg_prefix
        )
        self._test_data_integrity()

    def test_AvenantCommentsView_instructeur_ok(self):
        # login as user_instructeur_paris
        response = self.client.post(
            reverse("login"), {"username": "fix", "password": "654321"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path, self.success_payload)
        self.assertEqual(response.status_code, 302, msg=f"{self.msg_prefix}")
        self.assertRedirects(
            response, self.next_target_path, msg_prefix=self.msg_prefix
        )

    def test_AvenantCommentsView_instructeur_ko(self):
        # login as user_instructeur_metropole
        self.client.post(
            reverse("login"),
            {"username": "roger", "password": "567890"},
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")

    def test_AvenantCommentsView_bailleur_ok(self):
        # login as non bailleur user
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

    def test_AvenantCommentsView_bailleur_ko(self):
        # login as non bailleur user
        self.client.post(
            reverse("login"),
            {"username": "sophie", "password": "567890"},
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")


class ConventionCommentsViewTests(AvenantCommentsViewTests):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        self.convention_75 = Convention.objects.filter(numero="0001").first()
        self.target_path = reverse(
            "conventions:comments", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:recapitulatif", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/comments.html"
        self.error_payload = {"comments": "O" * 5001}
        self.success_payload = {"comments": "This is a comment"}
        self.msg_prefix = "[ConventionCommentsViewTests] "


class ConventionTypeStationnementViewTests(AvenantCommentsViewTests):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        self.convention_75 = Convention.objects.filter(numero="0001").first()
        self.target_path = reverse(
            "conventions:stationnements", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:comments", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/stationnements.html"
        self.error_payload = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-typologie": "GARAGE_AERIEN",
            "form-0-nb_stationnements": 30,
            "form-0-loyer": "",
            "form-1-uuid": "",
            "form-1-typologie": "GARAGE_ENTERRE",
            "form-1-nb_stationnements": "",
            "form-1-loyer": 100.00,
        }
        self.success_payload = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-0-uuid": "",
            "form-0-typologie": "GARAGE_AERIEN",
            "form-0-nb_stationnements": 30,
            "form-0-loyer": 12,
            "form-1-uuid": "",
            "form-1-typologie": "GARAGE_ENTERRE",
            "form-1-nb_stationnements": 5,
            "form-1-loyer": 10.00,
        }
        self.msg_prefix = "[ConventionTypeStationnementViewTests] "

    def _test_data_integrity(self):
        pass


class ConventionBailleurViewTests(AvenantCommentsViewTests):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        self.convention_75 = Convention.objects.filter(numero="0001").first()
        self.target_path = reverse(
            "conventions:bailleur", args=[self.convention_75.uuid]
        )
        self.next_target_path = reverse(
            "conventions:programme", args=[self.convention_75.uuid]
        )
        self.target_template = "conventions/bailleur.html"
        self.error_payload = {
            "nom": "",
            "adresse": "fake adresse",
            "code_postal": "00000",
        }
        self.success_payload = {
            "nom": "fake nom",
            "adresse": "fake adresse",
            "code_postal": "00000",
        }
        self.msg_prefix = "[ConventionBailleurViewTests] "

    def _test_data_integrity(self):
        self.convention_75.refresh_from_db()
        self.assertEqual(
            self.convention_75.bailleur.adresse,
            "fake adresse",
            msg=f"{self.msg_prefix}",
        )


class ConventionProgrammeViewTests(AvenantCommentsViewTests):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        self.convention_75 = Convention.objects.filter(numero="0001").first()
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
            "code_postal": "00000",
            "ville": "Fake ville",
            "nb_logements": "28",
            "anru": "FALSE",
            "type_habitat": "INDIVIDUEL",
            "type_operation": "NEUF",
            "nb_locaux_commerciaux": "",
            "nb_bureaux": "",
            "autres_locaux_hors_convention": "",
        }
        self.success_payload = {
            "nom": "Fake Opération",
            "adresse": "123 rue du fake",
            "code_postal": "00000",
            "ville": "Fake ville",
            "nb_logements": "28",
            "anru": "FALSE",
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
            "123 rue du fake",
            msg=f"{self.msg_prefix}",
        )
