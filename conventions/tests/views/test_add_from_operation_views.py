from django.test import TestCase
from django.urls import reverse


class TestSelectOperationView(TestCase):
    def _login(self):
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

    def test_search_filters_params(self):
        pass
