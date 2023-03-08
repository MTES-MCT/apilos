from django.test import TestCase
from django.urls import reverse

from core.tests import utils_fixtures


class UserViewTests(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs.json",
        "instructeurs.json",
        "programmes.json",
        "conventions.json",
        "users.json",
    ]

    def test_get_stats(self):
        """
        If not login, the request is not redirected and buton to login are displayed
        """
        self.assertEqual("/stats/", reverse("stats:index"))
        response = self.client.get(reverse("stats:index"))
        self.assertEqual(response.status_code, 200)
