from django.http.request import HttpRequest
from django.test import TestCase
from django.urls import reverse

from upload.views import _compute_dirpath


# @override_settings(CERBERE=None)
class UploadViewTest(TestCase):
    fixtures = [
        "auth.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self) -> None:
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

    def test_compute_dirpath(self):
        convention_uuid = "f590c593-e37f-4258-b38a-f8d2869969c4"
        request = HttpRequest()
        request.POST = {"convention": convention_uuid}
        dirpath = _compute_dirpath(request)
        self.assertEqual(dirpath, f"conventions/{convention_uuid}/media/")

        programme_uuid = "c3449e15-3739-4a35-8587-09be8c5ee007"
        request.POST = {"programme": programme_uuid}
        dirpath = _compute_dirpath(request)
        self.assertEqual(dirpath, f"programmes/{programme_uuid}/media/")

        lot_uuid = "09b07c04-a46a-4d41-a463-71b00c2d38ac"
        request.POST = {"lot": lot_uuid}
        dirpath = _compute_dirpath(request)
        self.assertEqual(dirpath, f"lots/{lot_uuid}/media/")
