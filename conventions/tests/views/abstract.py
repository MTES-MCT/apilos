from django.urls import reverse

from conventions.models import Convention


class AbstractCreateViewTestCase:
    # pylint: disable=E1101
    # Should be used with TestCase class as a Mixin class
    convention_75: Convention
    target_path: str
    next_target_starts_with: str | None = None
    target_template: str
    error_payload: dict
    success_payload: dict
    msg_prefix: str

    def setUp(self):
        self.convention_75 = Convention.objects.filter(numero="0001").first()
        self.target_path = ""
        self.next_target_path = ""
        self.target_template = ""
        self.error_payload = {}
        self.success_payload = {}
        self.msg_prefix = "[ViewTests] "

    def _test_data_integrity(self):
        pass

    def _test_redirect(self, response):
        if self.next_target_starts_with:
            self.assertTrue(response.url.startswith(self.next_target_starts_with))

    def test_view_not_logged(self):
        # user not logged -> redirect to login
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 302, msg=f"{self.msg_prefix}")
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={self.target_path}',
            msg_prefix=self.msg_prefix,
        )

    def test_view_superuser(self):
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
        self._test_redirect(response)
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

    def test_view_instructeur_ok(self):
        # login as user_instructeur_paris
        response = self.client.post(
            reverse("login"), {"username": "fix", "password": "654321"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path, self.success_payload)
        self.assertEqual(response.status_code, 302, msg=f"{self.msg_prefix}")
        self._test_redirect(response)

    def test_view_bailleur_ok(self):
        # login as non bailleur user
        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 200, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path, self.success_payload)
        self.assertEqual(response.status_code, 302, msg=f"{self.msg_prefix}")
        self._test_redirect(response)


class AbstractEditViewTestCase(AbstractCreateViewTestCase):
    # pylint: disable=E1101
    # Should be used with TestCase class as a Mixin class
    next_target_path: str

    def setUp(self):
        super().setUp()
        self.next_target_path = ""

    def _test_redirect(self, response):
        self.assertRedirects(
            response, self.next_target_path, msg_prefix=self.msg_prefix
        )

    def test_view_instructeur_ko(self):
        # login as user_instructeur_metropole
        self.client.post(
            reverse("login"),
            {"username": "roger", "password": "567890"},
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")

    def test_view_bailleur_ko(self):
        # login as non bailleur user
        self.client.post(
            reverse("login"),
            {"username": "sophie", "password": "567890"},
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")
