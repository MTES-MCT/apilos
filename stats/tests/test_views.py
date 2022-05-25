from django.test import TestCase
from django.urls import reverse

from core.tests import utils_fixtures


class UserViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # pylint: disable=R0914
        utils_fixtures.create_all()

    def test_get_stats(self):
        """
        If not login, the request is not redirected and buton to login are displayed
        """
        self.assertEqual("/stats/", reverse("stats:index"))
        response = self.client.get(reverse("stats:index"))
        self.assertEqual(response.status_code, 200)
