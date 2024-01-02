from django.test import TestCase
from django.urls import reverse


class ConventionViewsTests(TestCase):
    fixtures = [
        "auth.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def test_delete_convention_unknown_uuid(self):
        self.client.login(username="nicolas", password="12345")

        delete_path = reverse(
            "conventions:delete",
            kwargs={"convention_uuid": "b3d66d4e-0841-41a4-b643-4dcc37147391"},
        )

        response = self.client.post(delete_path)
        assert response.status_code == 403
