from django.test import TestCase
from django.urls import reverse


class UserViewTests(TestCase):
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

    def test_get_stats(self):
        """
        If not login, the request is not redirected and buton to login are displayed
        """
        self.assertEqual("/stats/", reverse("stats:index"))
        response = self.client.get(reverse("stats:index"))
        self.assertEqual(response.status_code, 200)
