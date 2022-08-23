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

    def test_AvenantCommentsView_not_logged(self):
        # user not logged -> redirect to login
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={self.target_path}',
        )

    def test_AvenantCommentsView_superuser(self):
        # login as superuser
        response = self.client.post(
            reverse("login"), {"username": "nicolas", "password": "12345"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            self.target_path,
            {"comments": "This is a comment"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("conventions:recapitulatif", args=[self.convention_75.uuid]),
        )
        self.convention_75.refresh_from_db()
        self.assertEqual(
            self.convention_75.comments, '{"files": [], "text": "This is a comment"}'
        )

    def test_AvenantCommentsView_instructeur_ok(self):
        # login as user_instructeur_paris
        response = self.client.post(
            reverse("login"), {"username": "fix", "password": "654321"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("conventions:recapitulatif", args=[self.convention_75.uuid]),
        )

    def test_AvenantCommentsView_instructeur_ko(self):
        # login as user_instructeur_metropole
        self.client.post(
            reverse("login"),
            {"username": "roger", "password": "567890"},
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 403)

    def test_AvenantCommentsView_bailleur_ok(self):
        # login as non bailleur user
        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("conventions:recapitulatif", args=[self.convention_75.uuid]),
        )

    def test_AvenantCommentsView_bailleur_ko(self):
        # login as non bailleur user
        self.client.post(
            reverse("login"),
            {"username": "sophie", "password": "567890"},
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 403)
